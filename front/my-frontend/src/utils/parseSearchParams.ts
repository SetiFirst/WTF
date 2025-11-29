  export function parseSearchParams(query: string): Array<{ key: string; value: string }> {
    if (!query) return [];

    const params = new URLSearchParams(query);
    const result: Array<{ key: string; value: string }> = [];

    params.forEach((value, key) => {
      result.push({ key, value });
    });

    return result;
  }