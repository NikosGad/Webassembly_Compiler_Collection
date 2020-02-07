export class CCompilationOptions {
  optimization_level: string;
  iso_standard: string;
  suppress_warnings: boolean;

  // constructor() {
  //     this.optimization_level = ""
  //     this.iso_standard = ""
  // }
}

export class CCompilationOptionsAllowedValues {
  optimization_level_allowed_values: string[] = [
      "O0",
      "O1",
      "O2",
      "O3",
      "Os",
      "Oz",
  ];

  iso_standard_allowed_values: string[] = [
    "c89",
    "c90",
    "c99",
    "c11",
    "c17",
    "gnu89",
    "gnu90",
    "gnu99",
    "gnu11",
    "gnu17",
  ];
}
