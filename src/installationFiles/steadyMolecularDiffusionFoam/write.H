if (runTime.writeTime())
{
	volVectorField gradY(fvc::grad(Y));

	volScalarField gradYx
	(
		IOobject
		(
			"gradYx",
			runTime.timeName(),
			mesh,
			IOobject::NO_READ,
			IOobject::AUTO_WRITE
		),
		gradY.component(vector::X)
	);

	volScalarField gradYy
	(
		IOobject
		(
			"gradYy",
			runTime.timeName(),
			mesh,
			IOobject::NO_READ,
			IOobject::AUTO_WRITE
		),
		gradY.component(vector::Y)
	);

	volScalarField gradYz
	(
		IOobject
		(
			"gradYz",
			runTime.timeName(),
			mesh,
			IOobject::NO_READ,
			IOobject::AUTO_WRITE
		),
		gradY.component(vector::Z)
	);

	volVectorField DYgradY
	(
		IOobject
		(
			"flux",
			runTime.timeName(),
			mesh,
			IOobject::NO_READ,
			IOobject::AUTO_WRITE
		),
		DY*gradY
	);

	runTime.write();
}
