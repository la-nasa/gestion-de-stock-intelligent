"""
Service Chatbot IA avec RAG (Retrieval-Augmented Generation).
Utilise LangChain, FAISS et Sentence Transformers.
"""
import os
import json
import pickle
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from app.utils.config import settings

logger = logging.getLogger(__name__)


class DocumentStore:
    """Stockage et indexation des documents pour le RAG."""
    
    def __init__(self, index_path: str = None):
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index = None
        self.embedding_model = None
        self.index_path = index_path or os.path.join(settings.MODELS_DIR, 'rag_index.pkl')
    
    def load_or_create_index(self):
        """Charge ou crée l'index FAISS."""
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            
            # Charger le modèle d'embedding
            model_name = settings.EMBEDDING_MODEL
            self.embedding_model = SentenceTransformer(model_name)
            
            # Essayer de charger l'index existant
            if os.path.exists(self.index_path):
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = data.get('embeddings')
                    if self.embeddings is not None:
                        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
                        self.index.add(self.embeddings.astype(np.float32))
                        logger.info(f"Index RAG chargé: {len(self.documents)} documents")
                        return
            
            # Créer un nouvel index avec des documents par défaut
            self._create_default_documents()
            self._build_index()
            
        except ImportError as e:
            logger.warning(f"Dépendances RAG non installées: {e}")
    
    def _create_default_documents(self):
        """Crée des documents par défaut sur le système d'inventaire."""
        self.documents = [
            {
                'id': 'doc_001',
                'title': 'Procédure d\'entrée de stock',
                'content': 'Pour créer une entrée de stock, allez dans Stocks > Entrées. '
                          'Sélectionnez l\'entrepôt, le fournisseur, et ajoutez les produits avec leurs quantités. '
                          'Validez ensuite l\'entrée pour mettre à jour les stocks.',
                'category': 'procedure',
            },
            {
                'id': 'doc_002',
                'title': 'Procédure de sortie de stock',
                'content': 'Les sorties de stock se font via Stocks > Sorties. '
                          'Indiquez le motif (usage interne, transfert, dommage), le département bénéficiaire, '
                          'et les produits à sortir. Une validation est nécessaire.',
                'category': 'procedure',
            },
            {
                'id': 'doc_003',
                'title': 'Gestion des inventaires',
                'content': 'Les inventaires permettent de vérifier l\'exactitude des stocks. '
                          'Créez une session d\'inventaire, comptez les articles physiquement, '
                          'et validez pour mettre à jour les quantités en base.',
                'category': 'procedure',
            },
            {
                'id': 'doc_004',
                'title': 'Commandes fournisseurs',
                'content': 'Pour commander, allez dans Commandes > Nouvelle commande. '
                          'Sélectionnez le fournisseur, ajoutez les produits et quantités souhaitées. '
                          'La commande doit être approuvée avant envoi au fournisseur.',
                'category': 'procedure',
            },
            {
                'id': 'doc_005',
                'title': 'Niveaux de stock',
                'content': 'Le stock minimum est le seuil d\'alerte. Le point de commande déclenche '
                          'une suggestion de réapprovisionnement. La quantité optimale est calculée '
                          'selon l\'historique de consommation.',
                'category': 'concept',
            },
            {
                'id': 'doc_006',
                'title': 'Rôles et permissions',
                'content': 'ADMIN: accès complet. MANAGER: gestion des opérations, validation. '
                          'SUPERVISOR: supervision, rapports. OPERATOR: opérations de base. '
                          'VIEWER: consultation seule. AUDITOR: logs et rapports d\'audit.',
                'category': 'concept',
            },
            {
                'id': 'doc_007',
                'title': 'QR Codes et Barcodes',
                'content': 'Chaque produit peut avoir un QR code et un code-barres. '
                          'Le QR code contient les informations du produit (ID, référence, nom). '
                          'Scannez pour accéder rapidement aux détails et au stock.',
                'category': 'feature',
            },
            {
                'id': 'doc_008',
                'title': 'Rapports disponibles',
                'content': 'Rapports disponibles: Niveau de stock, Mouvements, Consommation par département, '
                          'Inventaire. Formats: PDF, Excel, CSV. Générez depuis la section Rapports.',
                'category': 'feature',
            },
            {
                'id': 'doc_009',
                'title': 'Prévisions IA',
                'content': 'Le système utilise l\'IA pour prédire la consommation future. '
                          'Les modèles (Prophet, XGBoost, LSTM) analysent l\'historique et les tendances. '
                          'Les prévisions aident à anticiper les besoins d\'approvisionnement.',
                'category': 'feature',
            },
            {
                'id': 'doc_010',
                'title': 'Détection d\'anomalies',
                'content': 'Le système détecte automatiquement les anomalies: surconsommation, '
                          'vol potentiel, erreurs de stock, transferts suspects. '
                          'Les alertes sont envoyées aux managers pour investigation.',
                'category': 'feature',
            },
            {
                'id': 'doc_011',
                'title': 'Structure IUC',
                'content': 'L\'Institut Universitaire de la Côte (IUC) possède plusieurs campus. '
                          'Chaque campus a des départements et des entrepôts. '
                          'Les stocks sont gérés par campus et par entrepôt.',
                'category': 'organization',
            },
            {
                'id': 'doc_012',
                'title': 'Produits fréquents',
                'content': 'Produits couramment gérés: ordinateurs, projecteurs, imprimantes, '
                          'papier A4, fournitures de bureau, équipements de laboratoire, '
                          'mobilier, consommables informatiques.',
                'category': 'reference',
            },
        ]
    
    def _build_index(self):
        """Construit l'index FAISS."""
        import faiss
        
        texts = [doc['content'] for doc in self.documents]
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        
        # Créer l'index FAISS
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype(np.float32))
        
        # Sauvegarder
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'embeddings': self.embeddings,
            }, f)
        
        logger.info(f"Index RAG créé: {len(self.documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recherche les documents les plus pertinents."""
        if not self.embedding_model or self.index is None:
            return []
        
        # Encoder la requête
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)
        
        # Rechercher
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(1 / (1 + distances[0][i]))
                results.append(doc)
        
        return results
    
    def add_document(self, title: str, content: str, category: str = 'general'):
        """Ajoute un document à l'index."""
        doc = {
            'id': f'doc_{len(self.documents) + 1:03d}',
            'title': title,
            'content': content,
            'category': category,
        }
        self.documents.append(doc)
        self._build_index()


class LLMProvider:
    """Fournisseur LLM pour la génération de réponses."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = settings.LLM_MODEL
    
    def load_model(self):
        """Charge le modèle LLM."""
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            logger.info(f"Chargement du modèle {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            logger.info("Modèle LLM chargé avec succès")
            return True
        except ImportError:
            logger.warning("Transformers non installé")
            return False
        except Exception as e:
            logger.warning(f"Erreur chargement LLM: {e}. Utilisation du fallback.")
            return False
    
    def generate(self, prompt: str, max_length: int = 200) -> str:
        """Génère une réponse."""
        if self.model and self.tokenizer:
            try:
                inputs = self.tokenizer(prompt, return_tensors='pt', max_length=512, truncation=True)
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception:
                pass
        return None


class ChatbotService:
    """Service de chatbot avec RAG."""
    
    def __init__(self):
        self.doc_store = DocumentStore()
        self.llm = LLMProvider()
        self.llm_loaded = False
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.max_history = 10
        
        # Initialiser le store de documents
        self.doc_store.load_or_create_index()
    
    def initialize(self):
        """Initialise le chatbot (charge les modèles)."""
        self.llm_loaded = self.llm.load_model()
    
    def ask(self, question: str, user_id: str = None, language: str = 'fr') -> Dict[str, Any]:
        """Répond à une question."""
        
        # 1. Recherche RAG
        relevant_docs = self.doc_store.search(question, top_k=3)
        
        # 2. Déterminer l'intention
        intent = self._detect_intent(question)
        
        # 3. Construire le contexte
        context = self._build_context(question, relevant_docs, intent, user_id)
        
        # 4. Générer la réponse
        if self.llm_loaded:
            answer = self._generate_with_llm(question, context)
        else:
            answer = self._generate_with_rules(question, intent, relevant_docs)
        
        # 5. Générer des suggestions
        suggestions = self._generate_suggestions(question, intent)
        
        # 6. Sauvegarder l'historique
        if user_id:
            self._save_history(user_id, question, answer)
        
        return {
            'question': question,
            'answer': answer,
            'intent': intent,
            'confidence': self._estimate_confidence(relevant_docs, intent),
            'source': 'rag' if relevant_docs else 'rules',
            'relevant_docs': [
                {'title': d['title'], 'category': d['category'], 'score': d.get('score', 0)}
                for d in relevant_docs
            ],
            'suggestions': suggestions,
            'language': language,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _detect_intent(self, question: str) -> str:
        """Détecte l'intention de la question."""
        q = question.lower()
        
        intents = {
            'stock_check': ['combien', 'stock', 'reste', 'disponible', 'quantité', 'reste-t-il'],
            'stock_alert': ['rupture', 'épuisé', 'manque', 'bas', 'critique', 'alerte'],
            'consumption': ['consomme', 'dépense', 'utilise', 'coût', 'budget', 'consommation'],
            'order': ['commande', 'commander', 'réapprovisionner', 'achat', 'fournisseur'],
            'inventory': ['inventaire', 'compter', 'vérifier', 'physique'],
            'procedure': ['comment', 'procédure', 'faire', 'créer', 'étapes', 'comment faire'],
            'report': ['rapport', 'exporter', 'pdf', 'excel', 'csv', 'télécharger'],
            'anomaly': ['anomalie', 'suspect', 'vol', 'erreur', 'problème'],
            'forecast': ['prévision', 'futur', 'prédire', 'tendance', 'anticipation'],
            'general': ['aide', 'help', 'bonjour', 'salut', 'quoi', 'que'],
        }
        
        for intent, keywords in intents.items():
            if any(kw in q for kw in keywords):
                return intent
        
        return 'unknown'
    
    def _build_context(
        self, question: str, docs: List[Dict], intent: str, user_id: str = None
    ) -> str:
        """Construit le contexte pour la génération."""
        context_parts = []
        
        # Ajouter les documents pertinents
        if docs:
            context_parts.append("Informations pertinentes:")
            for doc in docs:
                context_parts.append(f"- {doc['title']}: {doc['content'][:200]}")
        
        # Ajouter l'historique de conversation
        if user_id and user_id in self.conversation_history:
            history = self.conversation_history[user_id][-3:]
            if history:
                context_parts.append("\nHistorique de conversation:")
                for h in history:
                    context_parts.append(f"Q: {h['question']}")
                    context_parts.append(f"R: {h['answer'][:100]}")
        
        return '\n'.join(context_parts)
    
    def _generate_with_llm(self, question: str, context: str) -> str:
        """Génère une réponse avec le LLM."""
        prompt = f"""Tu es l'assistant IA de l'Institut Universitaire de la Côte (IUC), 
spécialisé dans la gestion de stock.

Contexte:
{context}

Question: {question}

Réponse (en français, concise et utile):"""
        
        response = self.llm.generate(prompt, max_length=250)
        
        if response:
            return response.strip()
        
        # Fallback
        return self._generate_with_rules(question, 'unknown', [])
    
    def _generate_with_rules(
        self, question: str, intent: str, docs: List[Dict]
    ) -> str:
        """Génère une réponse basée sur des règles."""
        
        responses = {
            'stock_check': "Pour vérifier le stock, consultez la section Stocks > Vue d'ensemble. "
                          "Vous pouvez rechercher par produit, entrepôt ou catégorie. "
                          "Les quantités disponibles sont mises à jour en temps réel.",
            'stock_alert': "Les produits en alerte sont visibles dans le tableau de bord. "
                          "Vous recevez des notifications pour les stocks bas et les ruptures. "
                          "Le système suggère automatiquement les quantités à commander.",
            'consumption': "La consommation par département est disponible dans la section Analytiques. "
                          "Vous pouvez voir l'évolution mensuelle, les tops consommateurs, "
                          "et exporter les données.",
            'order': "Pour commander, allez dans Commandes > Nouvelle commande. "
                    "Sélectionnez le fournisseur, ajoutez les produits et quantités, "
                    "puis soumettez pour approbation.",
            'inventory': "Les inventaires se gèrent dans la section Inventaires. "
                        "Créez une session, comptez les articles, et validez. "
                        "Les écarts sont automatiquement calculés.",
            'procedure': "Vous trouverez les procédures détaillées dans la documentation. "
                        "Pour toute question spécifique, n'hésitez pas à me demander.",
            'report': "Les rapports sont disponibles dans la section Rapports. "
                     "Choisissez le type (stock, mouvements, consommation), le format (PDF, Excel, CSV), "
                     "et générez. Téléchargement automatique.",
            'anomaly': "Le système détecte automatiquement les anomalies de stock. "
                      "Consultez les alertes dans le tableau de bord. "
                      "Types: surconsommation, vol potentiel, erreurs, transferts suspects.",
            'forecast': "Les prévisions utilisent l'IA pour anticiper les besoins. "
                       "Le système analyse l'historique et les tendances. "
                       "Consultez les prévisions par produit dans la section Analytiques.",
            'general': "Je suis l'assistant IA de l'IUC Inventory System. Je peux vous aider avec :\n"
                      "• La vérification des stocks\n"
                      "• Les procédures (entrées, sorties, inventaires)\n"
                      "• Les commandes et fournisseurs\n"
                      "• Les rapports et analyses\n"
                      "• Les alertes et anomalies\n\n"
                      "Posez-moi votre question !",
        }
        
        base_response = responses.get(intent, responses['general'])
        
        # Enrichir avec les docs si disponibles
        if docs:
            doc_info = docs[0]
            base_response += f"\n\n📚 Voir aussi: {doc_info['title']}"
        
        return base_response
    
    def _generate_suggestions(self, question: str, intent: str) -> List[str]:
        """Génère des suggestions de questions."""
        suggestions_map = {
            'stock_check': [
                "Quels produits sont en rupture ?",
                "Quel est le produit le plus en stock ?",
                "Voir l'historique des mouvements",
            ],
            'stock_alert': [
                "Combien de produits sont en alerte ?",
                "Depuis quand ce produit est-il en rupture ?",
                "Qui a effectué la dernière commande ?",
            ],
            'consumption': [
                "Quel département consomme le plus ?",
                "Voir l'évolution sur 6 mois",
                "Comparer avec le mois dernier",
            ],
            'order': [
                "Voir les commandes en cours",
                "Quel fournisseur est le plus fiable ?",
                "Créer une nouvelle commande",
            ],
            'general': [
                "Combien reste-t-il d'ordinateurs ?",
                "Quels produits seront en rupture bientôt ?",
                "Quel département consomme le plus ?",
            ],
        }
        
        return suggestions_map.get(intent, suggestions_map['general'])[:3]
    
    def _estimate_confidence(self, docs: List[Dict], intent: str) -> float:
        """Estime la confiance de la réponse."""
        if not docs:
            return 0.3 if intent != 'unknown' else 0.1
        
        # Plus de docs = plus de confiance
        doc_score = min(len(docs) * 0.2, 0.5)
        
        # Score moyen des docs
        avg_score = np.mean([d.get('score', 0) for d in docs]) if docs else 0
        
        # Bonus si intention détectée
        intent_score = 0.2 if intent != 'unknown' else 0
        
        return min(doc_score + avg_score * 0.3 + intent_score, 0.95)
    
    def _save_history(self, user_id: str, question: str, answer: str):
        """Sauvegarde l'historique de conversation."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'question': question,
            'answer': answer[:200],
            'timestamp': datetime.now().isoformat(),
        })
        
        # Limiter la taille
        if len(self.conversation_history[user_id]) > self.max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Récupère l'historique de conversation."""
        return self.conversation_history.get(user_id, [])


# Instance globale
chatbot_service = ChatbotService()