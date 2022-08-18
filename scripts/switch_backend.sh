#!/bin/bash  
echo "Región dr activa $REGION_DR_ACTIVA..."
pip install boto3==1.20.22

if [ "$REGION_DR_ACTIVA" == "true" ]; then
	echo "Región que quedará activa $6 en $2"
	python scripts/switch_backend.py --ambiente "$2" --region_primaria "$4" --region_secundaria "$6"
else
	echo "Región que quedará activa $4 en $2"
	python scripts/switch_backend.py --ambiente "$2" --region_primaria "$6" --region_secundaria "$4"
fi