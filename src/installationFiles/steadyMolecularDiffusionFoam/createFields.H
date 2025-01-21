Info<< "Reading field Y\n" << endl;

volScalarField Y
(
    IOobject
    (
        "Y",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading diffusivity DY\n" << endl;

volScalarField DY
(
    IOobject
    (
        "DY",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimViscosity, Zero)
);

if (!DY.headerOk())
{
    Info<< "Reading transportProperties dictionary\n" << endl;

    IOdictionary transportProperties
    (
        IOobject
        (
            "transportProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    );

    // set constant diffusion coefficient from dictionary if DY field is not given
    DY = dimensionedScalar("DY", dimViscosity, transportProperties);
}

#include "createFvOptions.H"
