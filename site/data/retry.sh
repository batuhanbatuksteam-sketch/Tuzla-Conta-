#!/bin/bash
: "${REPLICATE_API_TOKEN:?once 'export REPLICATE_API_TOKEN=...' calistirin}"
# anahtar artik ortam degiskeninden okunur, dosyaya gomulmez
for i in 1 2 3 4 5 6 7 8; do
  P=$(ls ../assets/img/urun | wc -l); S=$(ls ../assets/img/sahne 2>/dev/null | wc -l)
  echo "=== tur $i — urun:$P/51 sahne:$S/19"
  [ "$P" -ge 51 ] && [ "$S" -ge 19 ] && { echo "TAMAM"; break; }
  python3 genimg.py 2>&1 | grep -vi atlandi
  python3 genscene.py 2>&1 | grep -vi atlandi
  sleep 20
done
echo "BITTI urun:$(ls ../assets/img/urun|wc -l) sahne:$(ls ../assets/img/sahne|wc -l)"
