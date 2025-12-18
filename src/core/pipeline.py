from .ports import Camera, Detector, Pipeline, CheckoutInput, CheckoutOutput
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

    def run_once(self) -> None:
        request = self.checkout_input.get_request()
        frame = self.camera.read()
        detections = self.detector.detect(frame)

        result = self.verifier.verify(detections, request)
        self.checkout_output.send_result(result)
