export type Result<T, E> =
  | { success: true; value: T }
  | { success: false; error: E };

export function isSuccess<T, E>(result: Result<T, E>): result is { success: true; value: T } {
  return result.success === true;
}

export function isError<T, E>(result: Result<T, E>): result is { success: false; error: E } {
  return result.success === false;
}
