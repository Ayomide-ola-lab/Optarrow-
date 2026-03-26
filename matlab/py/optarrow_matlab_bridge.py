import pyarrow as pa
import requests


def _dict_to_single_row_table(payload: dict) -> pa.Table:
    names = list(payload.keys())
    arrays = [pa.array([payload[name]]) for name in names]
    return pa.Table.from_arrays(arrays, names=names)


def _table_to_result_dict(table: pa.Table) -> dict:
    result = {}
    for name in table.column_names:
        values = table.column(name).to_pylist()
        result[name] = values[0] if len(values) == 1 else values
    return result


def compute_arrow_ipc(payload: dict, endpoint: str, timeout_sec: int = 120) -> dict:
    table = _dict_to_single_row_table(payload)

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write(table)

    ipc_bytes = sink.getvalue().to_pybytes()
    headers = {"Content-Type": "application/vnd.apache.arrow.stream"}

    response = requests.post(endpoint, data=ipc_bytes, headers=headers, timeout=timeout_sec)

    out = {
        "http_status": int(response.status_code),
        "success": bool(response.status_code == 200),
    }

    try:
        reader = pa.ipc.open_stream(response.content)
        result_table = reader.read_all()
        out.update(_table_to_result_dict(result_table))
    except Exception:
        try:
            out["error_message"] = response.text
        except Exception:
            out["error_message"] = "Unable to parse OptArrow response."

    return out
