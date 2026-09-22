function normalizedHistory(history) {
  return (Array.isArray(history) ? history : [])
    .filter(point => point && Number.isFinite(point.close) && point.date != null)
    .map(point => ({ ...point, date: String(point.date), close: Number(point.close) }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

export function computeSMA(closes, period) {
  const values = Array.isArray(closes) ? closes : [];
  if (!Number.isInteger(period) || period <= 0) return values.map(() => null);

  return values.map((_, index) => {
    if (index + 1 < period) return null;
    const window = values.slice(index + 1 - period, index + 1);
    if (!window.every(Number.isFinite)) return null;
    return window.reduce((sum, value) => sum + value, 0) / period;
  });
}

export function computePriceStats(history) {
  const points = normalizedHistory(history);
  if (!points.length) {
    return { latest: null, change: null, changePct: null, low: null, high: null, count: 0, startDate: null, endDate: null };
  }

  const closes = points.map(point => point.close);
  const first = closes[0];
  const latest = closes[closes.length - 1];
  const change = closes.length > 1 ? latest - first : null;
  const changePct = change != null && first !== 0 ? (change / first) * 100 : null;
  return {
    latest,
    change,
    changePct,
    low: Math.min(...closes),
    high: Math.max(...closes),
    count: points.length,
    startDate: points[0].date,
    endDate: points[points.length - 1].date,
  };
}

export function sliceRange(history, sessions) {
  const points = normalizedHistory(history);
  if (!Number.isFinite(sessions) || sessions <= 0) return points;
  return points.slice(-Math.floor(sessions));
}
