import { useEffect, useState, useCallback } from 'react';
import { errMsg } from '../utils/format';
export function useFetch(fn, deps = []) {
  const [data, setData] = useState(null), [loading, setLoading] = useState(true), [error, setError] = useState('');
  const load = useCallback(() => { setLoading(true); setError(''); fn().then(setData).catch((e) => setError(errMsg(e))).finally(() => setLoading(false)); }, deps); // eslint-disable-line
  useEffect(load, [load]);
  return { data, loading, error, reload: load, setData };
}
