export function useFormReset() {

  const resetForm = (formObject, additionalResetCallback = null) => {

    Object.keys(formObject).forEach(key => {
      formObject[key] = '';
    });

    if (additionalResetCallback) {
      additionalResetCallback();
    }
  };

  return { resetForm };
}
