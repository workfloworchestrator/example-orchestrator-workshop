from orchestrator.workflows import LazyWorkflowInstance

LazyWorkflowInstance("workflows.circuit.create_circuit", "create_circuit")
LazyWorkflowInstance("workflows.circuit.validate_circuit", "validate_circuit")
LazyWorkflowInstance("workflows.node.create_node", "create_node")
LazyWorkflowInstance("workflows.node.validate_node", "validate_node")
