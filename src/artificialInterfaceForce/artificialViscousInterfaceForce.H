/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2017 OpenFOAM Foundation
    Copyright (C) 2020 OpenCFD Ltd.
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

Class
    Foam::fv::artificialViscousInterfaceForce

Group
    grpFvOptionsSources

Description
	Artificial viscous term active at fluid interface 

SourceFiles
    artificialViscousInterfaceForce.C

\*---------------------------------------------------------------------------*/

#ifndef artificialViscousInterfaceForce_H
#define artificialViscousInterfaceForce_H

#include "autoPtr.H"
#include "fvMesh.H"
#include "volFields.H"
#include "cellSetOption.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace fv
{

/*---------------------------------------------------------------------------*\
               Class artificialViscousInterfaceForce Declaration
\*---------------------------------------------------------------------------*/

class artificialViscousInterfaceForce
:
    public fv::cellSetOption
{
protected:

    // Protected Data

		//- method for artificial viscosity calculation
		const word method_;

		//- constant artificial viscosity value for "constant" method
		const scalar interfaceViscosity_;

		//- method for gradient calculation
		const word gradMethod_;

		//- smoothing steps
		const scalar nSmoothingSteps_;

		//- smoothing coefficient
		const scalar smoothingCoeff_;

		IOdictionary transportProperties_;
		

    // Protected Member Functions

		//- Calculate artificial viscosity field
		fvMatrix<Vector<double>> calcAritificalInterfaceViscosity(const volVectorField& U);

        //- Write artificial viscosity, filterfield and normals to fields
        void writeToFields(volScalarField& avi, volScalarField& filterField, volVectorField& normals) const;


public:

    //- Runtime type information
    TypeName("artificialViscousInterfaceForce");


    // Constructors

        //- Construct from explicit source name and mesh
        artificialViscousInterfaceForce
        (
            const word& sourceName,
            const word& modelType,
            const dictionary& dict,
            const fvMesh& mesh
        );

        //- No copy construct
        artificialViscousInterfaceForce(const artificialViscousInterfaceForce&) = delete;

        //- No copy assignment
        void operator=(const artificialViscousInterfaceForce&) = delete;


    //- Destructor
    virtual ~artificialViscousInterfaceForce() = default;


    // Member Functions

        // Evaluation

            //- Correct the pressure gradient
            virtual void correct(volVectorField& U);

            //- Add explicit contribution to momentum equation
            virtual void addSup
            (
                fvMatrix<vector>& eqn,
                const label fieldi
            );

            //- Add explicit contribution to compressible momentum equation
            virtual void addSup
            (
                const volScalarField& rho,
                fvMatrix<vector>& eqn,
                const label fieldi
            );

            //- Set 1/A coefficient
            virtual void constrain
            (
                fvMatrix<vector>& eqn,
                const label fieldi
            );


        // IO

            //- Read source dictionary
            virtual bool read(const dictionary& dict);
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace fv
} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
