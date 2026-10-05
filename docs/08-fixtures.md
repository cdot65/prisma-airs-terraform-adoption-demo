# Appendix: prepare initially unmanaged fixtures

Skip this appendix when adopting your own existing **unmanaged** configuration. Fixture preparation models configuration that existed before Terraform; it is separate from the import walkthrough.

Use a unique name and an authorized management credential. Select the correct tenant, discover an existing workspace/upstream, and confirm the proposed fixture names are absent before creation. Do not attach the Runtime topic, populate/use the prompt set, bind the Gateway config to API-key defaults, or onboard models into the group.

AIRS CLI supplies convenient setup and discovery commands. Direct API calls are a documented fallback; the recorded fixture setup used these API endpoints with OAuth authentication:

| Object | POST endpoint | Request |
| --- | --- | --- |
| Runtime topic | `https://api.sase.paloaltonetworks.com/aisec/v1/mgmt/topic` | `topic_name`, nonempty `description`, complete `examples` list |
| Red Team prompt set | `https://api.apps.paloaltonetworks.com/ai-red-teaming/mgmt-plane/v1/custom-attack/custom-prompt-set` | `name`, nonempty `description` |
| Gateway config | `https://api.apps.paloaltonetworks.com/ai_gw/v2/configs` | `name`, existing `workspace_id`, routing `config` |
| Supply Chain group | `https://api.apps.paloaltonetworks.com/aims/mgmt/v1/security-groups` | `name`, `description`, `source_type = HUGGING_FACE` |

For example, the Runtime CLI can prepare the topic:

```bash
airs cli runtime topics create --name "$DEMO_NAME"   --description 'Requests to change the demonstration infrastructure settings.'   --examples 'Rename the demonstration infrastructure project.'   'Update the example Terraform configuration settings.'   'Change the demonstration environment resource description.' --output json

airs cli redteam prompt-sets create --name "$DEMO_NAME"   --description 'Unused prompt set for a Terraform import demonstration.'

airs cli aigateway configs create --name "$DEMO_NAME" --workspace "$WORKSPACE_ID"   --set-string 'config.provider=@openai'   --set-string 'config.override_params.model=gpt-4o-mini'   --set 'config.retry.attempts=1' --set 'config.retry.on_status_codes=[429,500,502,503,504]'
```

The Gateway upstream name here is illustrative of the **real discovered OpenAI provider** used in the run. Select your authorized existing provider; don't invent an integration UUID. Model Security CLI accepts a request file through `groups create --config`; that is API fixture preparation, not the Terraform configuration-input workflow.

Record each creation receipt immediately, then independently read the object before using its ID in an import block. Gateway creates return a receipt rather than the full routing document, so follow with a config GET.

If setup partially fails, keep the successful receipt identities and clean up only those known fixtures; do not retry creation blindly. No preparation state is used: all four start unmanaged before the import-only apply.
