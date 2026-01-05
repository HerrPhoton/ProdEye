from .dto import CheckoutRequest, VisualCheckStatus
from .ports import Camera, Detector, Pipeline, CheckoutInput, CheckoutOutput
from .ports import PipelineStepResult
from .services import VisualVerifier


class VisualVerificationPipeline(Pipeline):

    def __init__(
        self,
        camera: Camera,
        detector: Detector,
        verifier: VisualVerifier,
        checkout_input: CheckoutInput,
        checkout_output: CheckoutOutput,
    ):
        self.camera = camera
        self.detector = detector
        self.verifier = verifier
        self.checkout_input = checkout_input
        self.checkout_output = checkout_output

        self._active_request: CheckoutRequest | None = None

    def run_once(self) -> PipelineStepResult:
        """
        Выполняет один цикл визуальной проверки.

        Открывает новую сессию, если нет активного запроса от кассы.
        Закрывает активную сессию, если верификатор вернул финальный результат проверки.

        :return: Результат одного шага пайплайна.
        :rtype: PipelineStepResult
        """
        # Открытие сессии, если нет активного запроса
        if self._active_request is None:
            self._active_request = self.checkout_input.get_request()

        # Детекция товаров
        frame = self.camera.read()
        detections = self.detector.detect(frame)

        # Визуальная проверка и отправка результата
        result = self.verifier.verify(detections, self._active_request)
        self.checkout_output.send_result(result)

        # Закрытие сессии при финальном результате
        if result.status != VisualCheckStatus.PENDING:
            self._active_request = None

        return PipelineStepResult(
            frame=frame,
            detections=detections,
            result=result,
        )
