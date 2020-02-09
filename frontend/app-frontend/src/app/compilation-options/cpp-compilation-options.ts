export class CppCompilationOptions {
  optimization_level: string;
  iso_standard: string;
  suppress_warnings: boolean;
  output_filename: string;
}

export const CppCompilationOptionsAllowedValues = Object.freeze({
  optimization_level_allowed_values: [
      "O0",
      "O1",
      "O2",
      "O3",
      "Os",
      "Oz",
  ],

  iso_standard_allowed_values: [
    "c++98",
    "c++03",
    "c++11",
    "c++14",
    "c++17",
    "c++2a",
    "gnu++98",
    "gnu++03",
    "gnu++11",
    "gnu++14",
    "gnu+++17",
    "gnu+++2a",
  ],
})
