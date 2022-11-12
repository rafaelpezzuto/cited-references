class EmptyCitedJournalTitleError(Exception):
    ...


class EmptyCitedYearError(Exception):
    ...


class InvalidCitedVolumeError(Exception):
    ...


class VolumeIsUnknowError(Exception):
    ...


class LinearRegressionDoesNotExistError(Exception):
    ...


class ExactMatchTitleNotInCorrectionBaseError(Exception):
    ...


class ExactMatchValidationFailureError(Exception):
    ...


class FuzzyMatchTitleNotInCorrectionBaseError(Exception):
    ...


class ValidationIssnYearIsNotDigitError(Exception):
    ...


class GoldValidationFailureKeyDoesNotExistError(Exception):
    ...


class GoldValidationFaileureIssnOutOfListError(Exception):
    ...


class BronzeValidationFaileureIssnOutOfListError(Exception):
    ...


class SilverValidationFailureUndecidebleError(Exception):
    ...


class BronzeValidationFailureUndecidebleError(Exception):
    ...
