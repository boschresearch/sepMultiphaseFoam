/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2016 OpenFOAM Foundation
    Copyright (C) 2018-2021 OpenCFD Ltd.
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "artificialViscousInterfaceForce.H"
#include "fvMatrices.H"
#include "DimensionedField.H"
#include "IFstream.H"
#include "addToRunTimeSelectionTable.H"
#include "immiscibleIncompressibleTwoPhaseMixture.H"
#include "fvc.H"
#include "fvm.H"
#include "fvcSmooth.H"
#include "zeroGradientFvPatchFields.H"

// * * * * * * * * * * * * * Static Member Functions * * * * * * * * * * * * //

namespace Foam
{
namespace fv
{
    defineTypeNameAndDebug(artificialViscousInterfaceForce, 0);
    addToRunTimeSelectionTable(option, artificialViscousInterfaceForce, dictionary);
}
}


// * * * * * * * * * * * * Protected Member Functions  * * * * * * * * * * * //

void Foam::fv::artificialViscousInterfaceForce::writeToFields
(
	volScalarField& artificialViscosity,
	volScalarField& filterField,
	volVectorField& normals
) const
{
    
	volScalarField artificialViscosity_write
	(
	    IOobject
	    (
	        "avi",
	        mesh_.time().timeName(),
	        mesh_,
	        IOobject::NO_READ,
	        IOobject::AUTO_WRITE
	    ),
		artificialViscosity	
	);

	artificialViscosity_write.write();
    filterField.write();
    normals.write();


}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::fv::artificialViscousInterfaceForce::artificialViscousInterfaceForce
(
    const word& sourceName,
    const word& modelType,
    const dictionary& dict,
    const fvMesh& mesh
)
:
    fv::cellSetOption(sourceName, modelType, dict, mesh),
    method_(coeffs_.get<word>("method")),
    interfaceViscosity_(coeffs_.get<scalar>("value")), // only relevant for constant
	gradMethod_(coeffs_.get<word>("gradMethod")),
	nSmoothingSteps_(coeffs_.getOrDefault<scalar>("nSmoothingSteps",0)),
	smoothingCoeff_(coeffs_.getOrDefault<scalar>("smoothingCoeff",0)),
	transportProperties_
	(
	    IOobject
	    (   
	        "transportProperties",
	        mesh_.time().constant(),
			mesh_,
	        IOobject::MUST_READ_IF_MODIFIED,
	        IOobject::NO_WRITE
	    )   
	)
	
{
    coeffs_.readEntry("fields", fieldNames_);

	if (fieldNames_.size() != 1)
    {
        FatalErrorInFunction
            << "settings are:" << fieldNames_ << exit(FatalError);
    }
	
    fv::option::resetApplied();
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

Foam::fvMatrix<Foam::Vector<double>> Foam::fv::artificialViscousInterfaceForce::calcAritificalInterfaceViscosity
(
	const volVectorField& U
)
{
	// ------- 1. Gather necessary quantities -----------
	// (curvature, sigma, alpha1)
	
	// lookup curvature
	volScalarField curvature = mesh_.lookupObject<volScalarField>("interfaceProperties:K");

	// lookup sigma
	const dimensionedScalar sigma
    (
        "sigma",
        dimMass*pow(dimTime, -2),
        transportProperties_.lookupOrDefault("sigma",1.)
    );

	// lookup alpha
	List<word> phases(transportProperties_.lookup("phases"));
	volScalarField alpha1 = mesh_.lookupObject<volScalarField>("alpha." + phases[0]);


    // ---- 2. calculate filter field and normals ----
    // initialize fields
        volScalarField filterField
        (
            IOobject
            (
                "filterField",
                mesh_.time().timeName(),
                mesh_,
                IOobject::READ_IF_PRESENT,
                IOobject::AUTO_WRITE
            ),
			mesh_,
        	dimensionedScalar("SMALL", pow(dimLength, -1), SMALL), 
			zeroGradientFvPatchScalarField::typeName
        );

        volVectorField normals
        (
            IOobject
            (
                "normals",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::AUTO_WRITE
            ),
			mesh_,
			dimensionedVector("zeroVector", dimensionSet(0,0,0,0,0,0,0), Foam::vector(0,0,0))
        );
   

	// version 1 -  using grad(alpha)
	if (gradMethod_ == "grad")
	{
    	filterField = mag(fvc::grad(alpha1));
    	
		normals = fvc::grad(alpha1)/(filterField +
    	                               dimensionedScalar("SMALL", pow(dimLength, -1), SMALL)); 
	}

	// version 2 - using sngrad(alpha1), corrected with face areas
	else if (gradMethod_ == "snGrad")
	{
		filterField = mag(fvc::reconstruct(fvc::snGrad(alpha1) * mesh_.magSf()));
		
		normals = fvc::reconstruct(fvc::snGrad(alpha1) * mesh_.magSf()) /
									(filterField + dimensionedScalar("SMALL", pow(dimLength, -1.0), SMALL));
	}

	else	
    {
        FatalErrorInFunction
            << "Invalid method for gradient calculation:" << method_ <<  
			"\n valid methods are: grad, snGrad" << exit(FatalError);
    };
	
	// smooth filter field using average/interpolate
	for (label I = 0; I < nSmoothingSteps_; I++)
	{
		 filterField = fvc::average(fvc::interpolate(filterField));
	}

	// smooth filter field using smoothing function
	if (smoothingCoeff_ > SMALL)
	{
		fvc::smooth(filterField,smoothingCoeff_);
	
	}	

   // ---- 3. calculate artificial interface viscosity ----

	// initialize field
	volScalarField interfaceViscosity = filterField * 
				(dimensionedScalar("interfaceViscosity", dimMass*pow(dimTime, -1), interfaceViscosity_));

	// calculate artificial interface viscosity field
	if (method_ == "raessi")
	{
		interfaceViscosity = sigma * mesh_.time().deltaT() * filterField;
	}

	else if (method_ == "constant")
	{
		
		// normalize filter field
		forAll(filterField, I)
		{
			filterField[I] = filterField[I] * pow(mesh_.V()[I] , 1./3.);
		}
		
		filterField.correctBoundaryConditions();

		// calculate artificial interface viscosity
		interfaceViscosity = filterField * 
				(dimensionedScalar("interfaceViscosity", dimMass*pow(dimTime, -1), interfaceViscosity_));

	}

	else	
    {
        FatalErrorInFunction
            << "Invalid method for artificial interface viscosity calculation:" << method_ <<  
			"\n valid methods are: raessi, constant" << exit(FatalError);
    };

	
	// write interfaceViscosity, filterField, and normals
    if (mesh_.time().writeTime())
    {
		this->writeToFields(interfaceViscosity, filterField, normals); //LN
    };
	

   // ---- 4. calculate implicit term of surface tension ----
 
   // define Laplace-Beltrami of velocity as the full Laplace-operator
   // (implicit) and subtract the normal part (explicit)
    auto gradUTmp = fvc::grad(U);
    const auto& gradU = gradUTmp.ref();

    auto normalLaplacian = fvc::div((normals&gradU)*normals)
            - curvature*((gradU - ((normals&gradU)*normals))&normals);

	// implicit part of surface tension
    fvMatrix<Vector<double>> surfaceTensionImplicitPart = fvm::laplacian(interfaceViscosity, U)
                - interfaceViscosity*normalLaplacian;
	
	return surfaceTensionImplicitPart;
	
}

void Foam::fv::artificialViscousInterfaceForce::correct
(
	volVectorField& U
)
{
    //NotImplemented;
}


void Foam::fv::artificialViscousInterfaceForce::addSup
(
    fvMatrix<vector>& eqn,
    const label fieldi
)
{
	// lookup U 
	const volVectorField& U_ = mesh_.lookupObject<volVectorField>("U");

	// add implicit part of surface tension
	fvMatrix<Vector<double>> surfaceTensionImplicitPart = this->calcAritificalInterfaceViscosity(U_);
    eqn += surfaceTensionImplicitPart;
}

void Foam::fv::artificialViscousInterfaceForce::addSup
(
    const volScalarField& rho,
    fvMatrix<vector>& eqn,
    const label fieldi
)
{
    this->addSup(eqn, fieldi);
}


void Foam::fv::artificialViscousInterfaceForce::constrain
(
    fvMatrix<vector>& eqn,
    const label
)
{
    //NotImplemented;
}

bool Foam::fv::artificialViscousInterfaceForce::read(const dictionary& dict)
{
    NotImplemented;

    return false;
}


// ************************************************************************* //
