import { AbstractControl, FormGroup, ValidatorFn } from '@angular/forms';

export function shouldContainRegexpWithErrorName(reg_exp_str: string, reg_exp_error_name: string): ValidatorFn {
  return (control: AbstractControl): {[key: string]: any} | null => {
    if (!control.value) {
      return null;
    }

    const reg_exp = new RegExp(reg_exp_str);
    const reg_exp_found = reg_exp.test(control.value);

    if (reg_exp_found) {
      return null;
    }
    else {
      let result = {};
      result[reg_exp_error_name] = {requiredPattern: reg_exp_str, actualValue: control.value};
      return result;
    }
  };
}

export function fieldsShouldMatch(original_field: string, matching_field: string): ValidatorFn {
  return (fg: FormGroup): {[key: string]: any} | null => {
    const original_control = fg.controls[original_field];
    const matching_control = fg.controls[matching_field];

    if (!matching_control.value) {
      return null;
    }

    if (original_control.value !== matching_control.value) {
      let result = {};
      result[original_field + "Matching"] = {originalValue: original_control.value, matchingValue: matching_control.value};
      return result;
    }
    else {
      return null;
    }
  };
}
