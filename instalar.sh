#!/usr/bin/env bash
# Instala el comando `reviewer2` para abrir el juego desde cualquier carpeta.
#
#   ./instalar.sh          instala (o actualiza) el comando
#   ./instalar.sh --quitar lo elimina
#
# Crea un pequeño lanzador en ~/.local/bin que ejecuta reviewer2.py desde la
# carpeta donde está este repositorio. Si mueves el repositorio, vuelve a
# correr este script.

set -euo pipefail

DESTINO="${HOME}/.local/bin"
COMANDO="${DESTINO}/reviewer2"
VIEJO="${DESTINO}/revisor2"      # nombre anterior del juego
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--quitar" ]]; then
    rm -f "${COMANDO}" "${VIEJO}"
    echo "Comando reviewer2 eliminado."
    exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: se necesita python3." >&2
    exit 1
fi

mkdir -p "${DESTINO}"
cat > "${COMANDO}" <<EOF
#!/usr/bin/env bash
# Lanzador generado por ${REPO}/instalar.sh
exec python3 "${REPO}/reviewer2.py" "\$@"
EOF
chmod +x "${COMANDO}"
ln -sf "${COMANDO}" "${VIEJO}"
echo "Instalado: ${COMANDO} → ${REPO}/reviewer2.py"

case ":${PATH}:" in
    *":${DESTINO}:"*)
        echo "Listo. Escribe 'reviewer2' en cualquier terminal." ;;
    *)
        echo "Aviso: ${DESTINO} no está en tu PATH. Agrega esta línea a ~/.bashrc:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo "y abre una terminal nueva." ;;
esac
