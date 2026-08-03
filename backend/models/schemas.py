
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5
    document_id: str | None = None
    direct_retrieval: bool | None = False

class AnswerResponse(BaseModel):
    answer: str
    sources: list[dict]
    model_used: str

class QuizRequest(BaseModel):
    num_questions: int = 5
    difficulty: str = "medium"
    document_id: str | None = None

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    total: int
    difficulty: str

class FlashcardRequest(BaseModel):
    num_cards: int = 10
    document_id: str | None = None

class Flashcard(BaseModel):
    front: str
    back: str
    topic: str

class FlashcardsResponse(BaseModel):
    flashcards: list[Flashcard]
    total: int

class SummaryRequest(BaseModel):
    document_id: str | None = None
    length: str = "medium"

class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    word_count: int

class StudyPlanRequest(BaseModel):
    exam_date: str
    hours_per_day: float
    subjects: list[str]
    difficulty_level: str = "medium"

class StudyPlanResponse(BaseModel):
    plan: list[dict]
    total_days: int
    total_hours: float
    tips: list[str]

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks: int
    pages: int
