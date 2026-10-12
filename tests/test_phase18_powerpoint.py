from pptx import Presentation

from reports.powerpoint.generate_presentation import (
    OUTPUT_FILE,
    main,
)


def test_presentation_is_generated():
    main()
    assert OUTPUT_FILE.exists()


def test_presentation_has_eight_slides():
    main()
    presentation = Presentation(str(OUTPUT_FILE))
    assert len(presentation.slides) == 8


def test_presentation_has_expected_output_name():
    assert OUTPUT_FILE.name == "NEXUS-M_Executive_Briefing.pptx"