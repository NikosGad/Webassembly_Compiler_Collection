export class SourceCodeFile {
  id: number;
  user_id: number;
  name: string;
  directory: string;
  compilation_options: string[];
  language: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export const AvailableLanguages = [
  "C",
  "C++",
  "Golang",
];
