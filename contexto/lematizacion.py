import json
import spacy
from limpieza_texto import limpieza_basica
from lenguajes import detectar_lenguaje, definir_lenguaje

### Definir clases para el lematizador ###


class LematizadorSpacy():
    def __init__(self, lenguaje, dict_lemmas=None, dim_modelo='md'):
        """

        :param lenguaje:
        :param dict_lemmas:
        :param dim_modelo:
        """
        # Definir lenguaje del lematizador
        self.establecer_lenguaje(lenguaje)
        # Inicializar lematizador
        self.iniciar_lematizador(dim_modelo)
        # Si se introdujo un diccionario personalizado, se utiliza
        if isinstance(dict_lemmas, dict):
            self.modificar_lemmas(dict_lemmas)
        # Si es la ubicación del archivo, primero se carga
        elif isinstance(dict_lemmas, str):
            try:
                dict_lemmas = json.load(open(dict_lemmas))
                self.modificar_lemmas(dict_lemmas)
            except BaseException:
                print('No se pudo cargar el diccionario de lemas')

    def establecer_lenguaje(self, lenguaje):
        """

        :param lenguaje:
        :return:
        """
        self.lenguaje = definir_lenguaje(lenguaje)

    def iniciar_lematizador(self, dim_modelo):
        """

        :param dim_modelo:
        :return:
        """
        self.lematizador = None
        if self.lenguaje is not None:
            from utils.spacy_funcs import cargar_modelo
            self.lematizador = cargar_modelo(dim_modelo, self.lenguaje)

    def modificar_lemmas(self, dict_lemmas):
        """

        :param dict_lemmas:
        :return:
        """
        # Definir función auxiliar
        def cambiar_propiedades_lemma(doc):
            for token in doc:
                if(token.text in dict_lemmas):
                    token.lemma_ = dict_lemmas[token.text]
            return doc
        # Aplicar la función para modificar el lematizador
        if (self.lematizador is not None) and (self.lematizador != -1):
            self.lematizador.add_pipe(cambiar_propiedades_lemma, first=True)

    def lematizar(self, texto, limpiar=True):
        """

        :param texto:
        :param limpiar:
        :return:
        """
        if limpiar:
            texto = limpieza_basica(texto)
        return ' '.join([token.lemma_ for token in self.lematizador(texto)])

# Implementación alternativa, utilizando stanza


class LematizadorStanza():
    def __init__(
            self,
            lenguaje,
            modelo_lemas='',
            dict_lemmas=None,
            archivo_salida=''):
        # Definir lenguaje del lematizador
        self.establecer_lenguaje(lenguaje)
        # Inicializar lematizador
        self.iniciar_lematizador(modelo_lemas)
        # Si se introdujo un diccionario personalizado, se utiliza
        if isinstance(dict_lemmas, dict):
            self.modificar_lemmas(dict_lemmas, modelo_lemas, archivo_salida)
        # Si es la ubicación del archivo, primero se carga
        elif isinstance(dict_lemmas, str):
            try:
                dict_lemmas = json.load(open(dict_lemmas))
                self.modificar_lemmas(dict_lemmas)
            except BaseException:
                print('No se pudo cargar el diccionario de lemas')

    def establecer_lenguaje(self, lenguaje):
        """

        :param lenguaje:
        :return:
        """
        self.lenguaje = definir_lenguaje(lenguaje)

    def iniciar_lematizador(self, modelo_lemas):
        """

        :param modelo_lemas:
        :return:
        """
        from utils.stanza_funcs import stanza_pipeline
        self.lematizador = None
        if self.lenguaje is not None:
            self.lematizador = stanza_pipeline(
                self.lenguaje, modelo_lemas=modelo_lemas)

    def modificar_lemmas(
            self,
            dict_lemmas,
            archivo_entrada='',
            archivo_salida='',
            gpu=False):
        """

        :param dict_lemmas:
        :param archivo_entrada:
        :param archivo_salida:
        :param gpu:
        :return:
        """
        from utils.stanza_funcs import modificar_modelo
        self.lematizador = modificar_modelo(
            self.lematizador,
            'lemma',
            dict_lemmas,
            archivo_entrada,
            archivo_salida,
            gpu)

    def lematizar(self, texto, limpiar=True):
        """

        :param texto:
        :param limpiar:
        :return:
        """
        if limpiar:
            texto = limpieza_basica(texto)
        doc = self.lematizador(texto)
        # Extraer los lemas de cada palabra, de cada frase, y juntarlos
        return ' '.join([w.lemma for s in doc.sentences for w in s.words])


### Definir función que envuelva la funcionalidad básica de las clases ###

def lematizar_texto(
        texto,
        lenguaje='es',
        libreria='spacy',
        limpiar=True,
        lematizador=None,
        dict_lemmas=None,
        dim_modelo='md',
        modelo_lemas='',
        archivo_salida=''):
    """

    :param texto:
    :param lenguaje:
    :param libreria:
    :param limpiar:
    :param lematizador:
    :param dict_lemmas:
    :param dim_modelo:
    :param modelo_lemas:
    :param archivo_salida:
    :return:
    """
    # Si no se provee un lematizador, este debe ser inicializado
    if lematizador is None:
        if lenguaje == 'auto':
            lenguaje = detectar_lenguaje(texto)
        if libreria.lower() == 'spacy':
            lematizador = LematizadorSpacy(lenguaje, dict_lemmas, dim_modelo)
        elif libreria.lower() == 'stanza':
            lematizador = LematizadorStanza(
                lenguaje, modelo_lemas, dict_lemmas, archivo_salida)
        else:
            print(
                'Por favor escoja una librería válida para el lematizador (Spacy o Stanza)')
            return None
    # Si el lenguaje no se reconoce, se envía mensaje
    if lematizador.lematizador is None:
        print('Lenguaje no válido.')
        return None
    # Devolver la lematización del texto
    return lematizador.lematizar(texto, limpiar)
