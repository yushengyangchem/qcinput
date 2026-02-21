{
  buildPythonPackage,
  hatchling,
  gitignoreSource,
  lib,
}:
let
  versionFile = builtins.readFile ./src/qcinput/__init__.py;
  versionLine = builtins.replaceStrings [ "\n" "\r" ] [ "" "" ] versionFile;
  versionMatch = builtins.match ''.*__version__ = "([^"]+)".*'' versionLine;
  version =
    if versionMatch == null then
      throw "Cannot find __version__ in src/qcinput/__init__.py"
    else
      builtins.head versionMatch;
in
buildPythonPackage {
  pname = "qcinput";
  inherit version;
  src = gitignoreSource ./.;
  pyproject = true;

  build-system = [ hatchling ];

  nativeBuildInputs = [ ];

  dependencies = [ ];

  doCheck = true;
  pythonImportsCheck = [ "qcinput" ];
  meta = {
    description = "Generate quantum chemistry input files from molecular structures";
    homepage = "https://github.com/yushengyangchem/qcinput";
    license = lib.licenses.mit;
    mainProgram = "qcinput";
    maintainers = [
      {
        name = "Yusheng Yang";
        email = "yushengyangchem@gmail.com";
        github = "yushengyangchem";
      }
    ];
  };
}
