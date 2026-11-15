from musepy.client import MuseClient, MuseError

INVITE_CODE = "C5OF8S"

email = input("Correo para Muse: ").strip()
first_name = input("Nombre real: ").strip()
last_name = input("Apellido real: ").strip()
date_of_birth = input("Fecha de nacimiento (YYYY-MM-DD): ").strip()

c = MuseClient(
    proxy=None,
    impersonate="chrome142",
    lang="ja",
    timeout=30,
)

try:
    print("\n[1] Abriendo muse.ai...")
    r = c.open_home()
    print("HTTP:", r.status_code)

    print("[2] Iniciando registro...")
    c.restart()

    print("[3] Enviando OTP...")
    c.send_otp(email)

    otp = input("Código OTP recibido por correo: ").strip()

    print("[4] Confirmando OTP...")
    c.confirm_otp(otp)

    print("[5] Completando registro...")
    data = c.register_completion(
        date_of_birth=date_of_birth,
        first_name=first_name,
        last_name=last_name,
    )

    auth = data.get("auth_meta_session") or {}
    token = auth.get("frl_access_token")
    account_id = auth.get("frl_account_id")

    if not token:
        raise RuntimeError("Muse no devolvió frl_access_token")

    print("Cuenta:", account_id)

    print("[6] Activando sesión...")
    onboarding = c.activate_session(token)

    print("Destino:", onboarding.get("resolved_destination"))

    print("[7] Aceptando TOS...")
    c.accept_tos(onboarding)

    print("[8] Verificando acceso...")
    if not c.is_live():
        raise RuntimeError("La cuenta no tiene acceso activo a Muse/Hatch")

    print("[9] Inicializando VM...")
    vm_id = c.wake_vm()

    if not vm_id:
        raise RuntimeError("No se pudo obtener vmId")

    c.stateful_sharing()

    print("[10] Canjeando:", INVITE_CODE)
    ok, reason = c.redeem(INVITE_CODE)

    print("\n======================")
    print("CANJE:", ok)
    print("RESULTADO:", reason)
    print("======================")

except MuseError as e:
    print("\nERROR DE MUSE:", e)

except Exception as e:
    print("\nERROR:", e)

finally:
    c.close()