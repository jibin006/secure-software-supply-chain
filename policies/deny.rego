# Wrong version first — intentional failure
# policies/deny_ssh_world.rego.wrong
package terraform.security

# WRONG: This path does not exist in terraform plan JSON
deny[msg] {
  resource := input.resource.aws_security_group[_]  # WRONG PATH
  ingress := resource.ingress[_]
  ingress.cidr_blocks[_] == "0.0.0.0/0"
  ingress.from_port == 22
  msg := sprintf("Security group allows SSH from world: %v", [resource])
}