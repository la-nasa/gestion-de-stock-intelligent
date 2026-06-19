"""Routes du chatbot IA avec RAG."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.chatbot_service import chatbot_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Requête de chat."""
    question: str
    context: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "fr"


class ChatResponse(BaseModel):
    """Réponse du chatbot."""
    question: str
    answer: str
    intent: str
    confidence: float
    source: str
    relevant_docs: List[Dict[str, Any]]
    suggestions: List[str]
    language: str
    timestamp: str


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """Pose une question au chatbot IA."""
    try:
        result = chatbot_service.ask(
            question=request.question,
            user_id=request.user_id,
            language=request.language,
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions(
    query: str = Query("", description="Texte partiel pour suggestions"),
    language: str = Query("fr", description="Langue"),
):
    """Suggestions de questions fréquentes."""
    
    all_suggestions = {
        'fr': [
            "Combien reste-t-il d'ordinateurs Dell ?",
            "Quels produits sont en rupture de stock ?",
            "Quel département consomme le plus ?",
            "Quel est le fournisseur le plus fiable ?",
            "Comment créer une entrée de stock ?",
            "Quels produits seront en rupture dans deux mois ?",
            "Quelle est la valeur totale du stock ?",
            "Combien de commandes sont en attente ?",
            "Comment générer un rapport d'inventaire ?",
            "Quels produits n'ont pas bougé depuis 6 mois ?",
        ],
        'en': [
            "How many Dell computers are left?",
            "Which products are out of stock?",
            "Which department consumes the most?",
            "Who is the most reliable supplier?",
            "How to create a stock entry?",
            "Which products will be out of stock soon?",
            "What is the total stock value?",
            "How many orders are pending?",
        ],
    }
    
    suggestions = all_suggestions.get(language, all_suggestions['fr'])
    
    # Filtrer si query
    if query:
        q = query.lower()
        suggestions = [s for s in suggestions if q in s.lower()]
    
    return {
        'suggestions': suggestions[:8],
        'language': language,
        'categories': [
            {'name': 'Stock', 'icon': 'Package'},
            {'name': 'Commandes', 'icon': 'ShoppingCart'},
            {'name': 'Rapports', 'icon': 'FileText'},
            {'name': 'Procédures', 'icon': 'HelpCircle'},
        ],
    }


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    """Historique de conversation d'un utilisateur."""
    history = chatbot_service.get_conversation_history(user_id)
    
    return {
        'user_id': user_id,
        'conversations': history,
        'count': len(history),
    }


@router.delete("/history/{user_id}")
async def clear_history(user_id: str):
    """Efface l'historique de conversation."""
    if user_id in chatbot_service.conversation_history:
        del chatbot_service.conversation_history[user_id]
    
    return {
        'status': 'success',
        'message': 'Historique effacé',
    }


@router.post("/documents")
async def add_document(
    title: str,
    content: str,
    category: str = "general",
):
    """Ajoute un document à la base de connaissances."""
    chatbot_service.doc_store.add_document(title, content, category)
    
    return {
        'status': 'success',
        'message': f"Document '{title}' ajouté à l'index",
        'total_documents': len(chatbot_service.doc_store.documents),
    }


@router.get("/health")
async def chatbot_health():
    """État du chatbot."""
    return {
        'status': 'healthy',
        'llm_loaded': chatbot_service.llm_loaded,
        'model_name': chatbot_service.llm.model_name,
        'documents_count': len(chatbot_service.doc_store.documents),
        'active_conversations': len(chatbot_service.conversation_history),
    }