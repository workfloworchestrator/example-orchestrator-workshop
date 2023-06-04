# folders for generated code
PRODUCTS_PATH="products"
export PRODUCT_TYPES_PATH="${PRODUCTS_PATH}/product_types"
export PRODUCT_BLOCKS_PATH="${PRODUCTS_PATH}/product_blocks"
export WORKFLOWS_PATH="workflows"
export TEST_PRODUCT_TYPE_PATH="test/unit_tests/domain/product_types"
export TEST_WORKFLOWS_PATH="test/unit_tests/workflows"
# files that are updated
export SUBSCRIPTION_DESCRIPTION_PATH="products/services/subscription.py"
TRANSLATION_FOLDER="translations"
export TRANSLATION_PATH="${TRANSLATION_FOLDER}/en-GB.json"

mkdir -pv "${PRODUCT_TYPES_PATH}" "${PRODUCT_BLOCKS_PATH}" "${WORKFLOWS_PATH}" "${TEST_PRODUCT_TYPE_PATH}" "${TEST_WORKFLOWS_PATH}" "${TRANSLATION_FOLDER}"

PRODUCTS_INIT_FILE="${PRODUCTS_PATH}/__init__.py"
if test ! -f "${PRODUCTS_INIT_FILE}"
then
    echo "from orchestrator.domain import SUBSCRIPTION_MODEL_REGISTRY" >> "${PRODUCTS_INIT_FILE}"
fi
WORKFLOWS_INIT_FILE="${WORKFLOWS_PATH}/__init__.py"
if test ! -f "${WORKFLOWS_INIT_FILE}"
then
    echo "from orchestrator.workflows import LazyWorkflowInstance" >> "${WORKFLOWS_INIT_FILE}"
fi

#for CONFIG_FILE in product_models/circuit.yaml
for CONFIG_FILE in node.yaml circuit.yaml
do
    set -x
    export PYTHONPATH=/Users/hanst/Sources/workfloworchestrator/orchestrator-core:.
    for ACTION in product-blocks product workflows migration unit-tests
    do
        python main.py generate "${ACTION}" --config-file "${CONFIG_FILE}" --no-dryrun --force
    done
done
