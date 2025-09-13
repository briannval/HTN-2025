#!/bin/bash
LAYER_NAME="htn_lambda_layer"
rm -rf $LAYER_NAME
rm -f ${LAYER_NAME}.zip
mkdir -p $LAYER_NAME/python
pip install opensearch-py requests_aws4auth -t $LAYER_NAME/python
cd $LAYER_NAME
zip -r ../${LAYER_NAME}.zip .
cd ..
echo "${LAYER_NAME}.zip created"
