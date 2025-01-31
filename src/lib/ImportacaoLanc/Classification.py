from dataclasses import dataclass
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


@dataclass
class TrainingData:
    descricao: str
    valor: float
    categoria: str


class LancamentosClassificador:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.label_encoder = None

    # def load_data(self):
    #     """Carrega dados incluindo valor e descrição"""
    #     df = pd.read_csv(
    #         "training.csv",
    #         sep=";",
    #         names=["descricao", "categoria", "valor"],
    #         decimal=",",
    #     )
    #     return df

    def preprocess_text(self, series):
        """Pré-processamento do texto"""
        return series.str.lower().str.replace("[^\w\s]", "", regex=True)

    def build_preprocessor(self):
        """Cria um pré-processador combinando texto e valor"""
        return ColumnTransformer(
            [
                (
                    "text",
                    TfidfVectorizer(ngram_range=(1, 2), max_features=1000),
                    "descricao",
                ),
                (
                    "valor",
                    Pipeline(
                        [
                            (
                                "selector",
                                FunctionTransformer(
                                    lambda df: df["valor"].values.reshape(-1, 1),
                                    validate=False,
                                ),
                            ),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    ["descricao", "valor"],
                ),
            ]
        )

    def train_model(self, data: list[TrainingData]):
        """Treina o modelo com múltiplas features"""
        # df = self.load_data()
        df = pd.DataFrame(data)

        # Pré-processamento
        df["descricao"] = self.preprocess_text(df["descricao"])
        df["valor"] = df["valor"].abs()  # Valor absoluto

        # Codificar categorias
        self.label_encoder = LabelEncoder()
        categoria_lbl_enc = self.label_encoder.fit_transform(df["categoria"])

        # Criar pré-processador
        self.preprocessor = self.build_preprocessor()

        # Criar pipeline completo
        self.model = Pipeline(
            [
                ("preprocessor", self.preprocessor),
                ("classifier", SVC(kernel="linear", probability=True)),
            ]
        )

        # Treinar
        df_descr_valor = df[["descricao", "valor"]]
        X_train, X_test, y_train, y_test = train_test_split(
            df_descr_valor, categoria_lbl_enc, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)

        # Avaliar
        y_pred = self.model.predict(X_test)
        print(
            classification_report(
                y_test,
                y_pred,  # , target_names=self.label_encoder.classes_
            )
        )

    def predict_category(self, description, value):
        """
        Classifica uma nova transação com valor

        Retorna:
        --------
        categoria
        confiabilidade
        """
        if not self.model:
            raise ValueError("Modelo não foi treinado")

        # Criar DataFrame de entrada
        input_data = pd.DataFrame([[description, abs(float(value))]], columns=["descricao", "valor"])

        # Pré-processar texto
        input_data["descricao"] = self.preprocess_text(input_data["descricao"])

        # Fazer predição
        probas = self.model.predict_proba(input_data)[0]
        predicted_index = self.model.predict(input_data)[0]
        confidence = probas.max()

        return (
            self.label_encoder.inverse_transform([predicted_index])[0],
            round(float(confidence * 100), 4),
        )
