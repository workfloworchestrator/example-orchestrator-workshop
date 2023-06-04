from orchestrator.workflows import LazyWorkflowInstance

LazyWorkflowInstance("surf.workflows.node.create_node", "create_node")
LazyWorkflowInstance("surf.workflows.node.modify_node", "modify_node")
LazyWorkflowInstance("surf.workflows.node.terminate_node", "terminate_node")
LazyWorkflowInstance("surf.workflows.node.validate_node", "validate_node")
LazyWorkflowInstance("surf.workflows.circuit.create_circuit", "create_circuit")
LazyWorkflowInstance("surf.workflows.circuit.modify_circuit", "modify_circuit")
LazyWorkflowInstance("surf.workflows.circuit.terminate_circuit", "terminate_circuit")
LazyWorkflowInstance("surf.workflows.circuit.validate_circuit", "validate_circuit")