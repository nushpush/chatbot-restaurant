import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import TextCategory
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions
from utils.keys import key
keys = key()

content_safety_endpoint = keys["AZURE_CONTENT_SAFETY_ENDPOINT"]
content_safety_key = keys["AZURE_CONTENT_SAFETY_KEY"]

def analyze_content(content):
    client_new = ContentSafetyClient(content_safety_endpoint, AzureKeyCredential(content_safety_key))
    request = AnalyzeTextOptions(text = content)
    try:
        response = client_new.analyze_text(request)
    except HttpResponseError as e:
        if e.error:
            raise
        raise

    hate_result = next(item for item in response.categories_analysis if item.category == TextCategory.HATE)
    self_harm_result = next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM)
    sexual_result = next(item for item in response.categories_analysis if item.category == TextCategory.SEXUAL)
    violence_result = next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE)
    return {
        'hate_result': hate_result,
        'self_harm_result': self_harm_result,
        'sexual_result': sexual_result,
        'violence_result': violence_result
    }
