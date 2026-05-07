# policies/deny_ssh_world.rego
package terraform.security

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_security_group"
  ingress := resource.values.ingress[_]
  ingress.cidr_blocks[_] == "0.0.0.0/0"
  ingress.from_port <= 22
  ingress.to_port >= 22

  msg := sprintf(
    "POLICY VIOLATION: Security group '%v' allows SSH (port 22) from 0.0.0.0/0. Blast radius: any internet host can attempt authentication against instances in this group.",
    [resource.name]
  )
}