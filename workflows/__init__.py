from orchestrator.workflows import LazyWorkflowInstance

LazyWorkflowInstance("workflows.user_group.create_user_group", "create_user_group")
LazyWorkflowInstance("workflows.user_group.modify_user_group", "modify_user_group")
LazyWorkflowInstance("workflows.user_group.terminate_user_group", "terminate_user_group")
LazyWorkflowInstance("workflows.user.create_user", "create_user")
LazyWorkflowInstance("workflows.user.modify_user", "modify_user")
LazyWorkflowInstance("workflows.user.terminate_user", "terminate_user")
LazyWorkflowInstance("workflows.circuit.create_circuit", "create_circuit")
LazyWorkflowInstance("workflows.circuit.validate_circuit", "validate_circuit")
LazyWorkflowInstance("workflows.node.create_node", "create_node")
LazyWorkflowInstance("workflows.node.validate_node", "validate_node")
