import requests

def lambda_handler(event, context):
    # API Text to Speech
    tts_api_url = "https://l0zf2fb0k3.execute-api.us-east-1.amazonaws.com/v1/tts"
            
    # Slack Web Hook
    slack_webhook_url = "https://hooks.slack.com/services/<YOUR_WEBHOOK>"
    
    # Get intent name
    intent_name = event['sessionState']['intent']['name']
    print("Intent Name: ",intent_name)
    
    if intent_name == 'BookTicket':
        # Get slots
        slots = event['sessionState']['intent']['slots']
        print("Slots: ",slots)
        
        destino = slots.get('Destino', {}).get('value', {}).get('interpretedValue', '')
        tipo_passagem = slots.get('TpPassagem', {}).get('value', {}).get('interpretedValue', '')
        primeiro_nome = slots.get('SeuPnome', {}).get('value', {}).get('interpretedValue', '')
        data_viagem = slots.get('data', {}).get('value', {}).get('interpretedValue', '')
        tipo_pagamento = slots.get('Pagamento', {}).get('value', {}).get('interpretedValue', '')

        # All slots filled
        if all([destino, tipo_passagem, primeiro_nome, data_viagem, tipo_pagamento]):
            # Custom message
            message = "Perfeito! Sr. %s, sua passagem para %s na categoria %s, no %s para o dia %s foi reservada com sucesso!" % (primeiro_nome, destino, tipo_passagem,tipo_pagamento, data_viagem)
            print("Message sent to TTS API: ",message)
            
            # Post API Text to Speech
            tts_payload = {
                "phrase": message
            }
            tts_response = requests.post(tts_api_url, json=tts_payload)
            tts_response_data = tts_response.json()
            audio_url = tts_response_data['url_to_audio']
    
            # Post Slack Webhook
            slack_message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "🔉 Clique para gerar a confirmação em formato de áudio"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Ouvir Áudio",
                                "emoji": True
                            },
                            "url": audio_url,
                            "action_id": "button-action"
                        }
                    }
                ]
            }
            requests.post(slack_webhook_url, json=slack_message)
        
        # Return Delegate to Lex
        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    "name": event['sessionState']['intent']['name'],
                    "state": "InProgress",
                    "slots": event['sessionState']['intent']['slots']
                }
            }
        }

    return response