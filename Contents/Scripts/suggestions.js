function runWithString(input) {
    // 定義支援補全的關鍵字清單
    const keywords = [
        'filesystem',
        'fetch',
        'tavily_search',
        'shell',
        'spotify-edit',
        'spotify-play',
        'things',
        'calendar'
    ];

    // 搜尋輸入字串中最後一個 @ 符號的位置
    const atIndex = input.lastIndexOf('@');

    if (atIndex !== -1) {
        // 從 @ 符號後提取可能的查詢文字，這裡以非空白字元為依據
        const remainder = input.slice(atIndex + 1);

        // 若使用者可能輸入了部分文字，但遇到空格就代表結束該區段
        const queryMatch = remainder.match(/^\S*/);
        const query = queryMatch ? queryMatch[0] : '';

        // 過濾出符合查詢條件的補全選項
        const matches = keywords.filter(keyword => keyword.startsWith(query));

        // 將補全結果整合進原句中
        return matches.map(keyword => {
            // 替換從 @ 符號開始，到 query 結束位置的部分
            const suggestion = input.slice(0, atIndex + 1) + keyword + input.slice(atIndex + 1 + query.length);
            return { title: suggestion };
        });
    }

    // 若輸入字串中沒有 @，則維持原有的補全邏輯
    // return [
    //   { title: input }
    // ];
}
