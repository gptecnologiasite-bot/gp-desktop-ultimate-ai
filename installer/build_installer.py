"""Generator de script Inno Setup (.iss) para o GP Desktop Ultimate AI.

Apenas gera texto; nao executa o Inno Setup. O .iss resultante pode ser
compilado com o ISCC.exe do Inno Setup.

Uso:
    python installer/build_installer.py
    python installer/build_installer.py --version 1.0.0 --output installer/MeuApp.iss
"""

from __future__ import annotations

import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "1.0.0"
APP_NAME = "GP Desktop Ultimate AI"
APP_EXE = "GPDesktopUltimateAI.exe"


def generate_iss(version: str, source_dir: Path, output_path: Path) -> str:
    src = str(source_dir).replace("\\", "\\\\")
    content = (
        '; Inno Setup script gerado por installer/build_installer.py\n'
        '#define MyAppName "' + APP_NAME + '"\n'
        '#define MyAppVersion "' + version + '"\n'
        '#define MyAppPublisher "GP"\n'
        '#define MyAppExeName "' + APP_EXE + '"\n'
        '\n'
        '[Setup]\n'
        'AppId={{8F2C1A3B-4D5E-6F70-8192-A3B4C5D6E7F8}}\n'
        'AppName={#MyAppName}\n'
        'AppVersion={#MyAppVersion}\n'
        'AppPublisher={#MyAppPublisher}\n'
        'DefaultDirName={autopf}\\{#MyAppName}\n'
        'DefaultGroupName={#MyAppName}\n'
        'OutputBaseFilename=GPDesktopUltimateAI-Setup-' + version + '\n'
        'Compression=lzma\n'
        'SolidCompression=yes\n'
        'WizardStyle=modern\n'
        'ArchitecturesAllowed=x64\n'
        'ArchitecturesInstallIn64BitMode=x64\n'
        'DisableProgramGroupPage=yes\n'
        '\n'
        '[Languages]\n'
        'Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.isl"\n'
        '\n'
        '[Tasks]\n'
        'Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked\n'
        '\n'
        '[Files]\n'
        'Source: "' + src + '\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs\n'
        '\n'
        '[Icons]\n'
        'Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"\n'
        'Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon\n'
        '\n'
        '[Run]\n'
        'Filename: "{app}\\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent\n'
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera .iss do Inno Setup")
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--source",
        default=str(BASE_DIR / "dist" / "GPDesktopUltimateAI"),
        help="Diretorio de origem (build onedir)",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "installer" / "GPDesktopUltimateAI.iss"),
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    output_path = Path(args.output)
    generate_iss(args.version, source_dir, output_path)
    print(f"Script Inno Setup gerado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
