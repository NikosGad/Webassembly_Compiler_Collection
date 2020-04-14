export class SourceCodeFile {
  name: string;
  language: string;
  options: string;
  status: string;
  path: string;
  content: string;
};

export const AvailableLanguages = [
  "C",
  "C++",
  "Golang",
];
