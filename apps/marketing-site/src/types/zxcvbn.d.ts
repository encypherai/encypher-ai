declare module 'zxcvbn' {
  interface ZXCVBNResult {
    score: number;
    feedback: {
      warning: string;
      suggestions: string[];
    };
    // Add more fields as needed
  }
  function zxcvbn(password: string): ZXCVBNResult;
  export = zxcvbn;
}
