import json
from musepy.client import MuseClient, MuseError

INVITE_CODE = "C5OF8S"


def resumen(data):
    campos = (
        "registration_state",
        "flow",
        "password_login_available",
        "has_muse_account",
        "redirect_to",
    )
    return {k: data.get(k) for k in campos if k in data}


email = input("Correo de la cuenta existente: ").strip()

c = MuseClient(
    proxy=None,
    impersonate="chrome142",
    lang="en-US",
    timeout=30,
)

try:
    print("\n[1] Abriendo Muse...")
    r = c.open_home()
    print("HTTP:", r.status_code)

    print("[2] Iniciando sesión native-auth...")
    c.restart()

    print("[3] Consultando cuenta / enviando OTP...")
    send = c.send_otp(email)

    print("Estado:", resumen(send))

    flow = send.get("flow")
    has_account = send.get("has_muse_account")
    password_available = send.get("password_login_available")

    print("flow =", flow)
    print("has_muse_account =", has_account)
    print("password_login_available =", password_available)

    # IMPORTANTE:
    # este archivo es únicamente para reanudar cuentas existentes.
    if flow != "login":
        print("\nMuse no está devolviendo flow=login.")
        print("NO se ejecutará register_completion().")
        raise SystemExit(2)

    if password_available is True:
        print("\nEsta cuenta tiene login por contraseña disponible.")
        print("No voy a intentar registrarla nuevamente.")
        print("Hace falta implementar confirm-password para esta cuenta.")
        raise SystemExit(3)

    otp = input("Código OTP recibido por correo: ").strip()

    print("[4] Confirmando OTP...")
    confirm = c.confirm_otp(otp)

    print("\nRESPUESTA COMPLETA CONFIRM-OTP:")
    print(json.dumps(confirm, indent=2, ensure_ascii=False))

    # Algunas variantes de login pueden entregar directamente
    # auth_meta_session después del OTP.
    auth = confirm.get("auth_meta_session") or {}

    token = auth.get("frl_access_token")
    account_id = auth.get("frl_account_id")

    if not token:
        print("\n======================================")
        print("OTP ACEPTADO, PERO NO HAY SESIÓN FRL")
        print("======================================")
        print("Muse reconoce la cuenta existente,")
        print("pero confirm-otp no devolvió frl_access_token.")
        print()
        print("NO se llamará register_completion().")
        print("La siguiente ruta sería recovery/password login.")
        raise SystemExit(4)

    print("Cuenta:", account_id)

    print("[5] Bootstrap de sesión...")
    onboarding = c.activate_session(token)

    print("state =", onboarding.get("state"))
    print("resolved_destination =", onboarding.get("resolved_destination"))
    print("is_geo_gated =", onboarding.get("is_geo_gated"))
    print("has_hatch_access =", onboarding.get("has_hatch_access"))
    print("waitlist_status =", onboarding.get("waitlist_status"))

    state = onboarding.get("state")

    if state == "disclosure":
        print("[6] Aceptando TOS...")
        c.accept_tos(onboarding)

    elif state == "active":
        print("[6] Cuenta ya activa; no es necesario aceptar TOS nuevamente.")

    else:
        raise RuntimeError(f"Estado de onboarding inesperado: {state}")

    print("[7] Comprobando Hatch...")
    if not c.is_live():
        raise RuntimeError("Muse no devuelve acceso activo a Hatch")

    print("[8] Wake VM...")
    vm_id = c.wake_vm()

    print("vm_id =", vm_id)

    if not vm_id:
        raise RuntimeError("No se pudo obtener vmId")

    c.stateful_sharing()

    print("[9] Canjeando:", INVITE_CODE)
    ok, reason = c.redeem(INVITE_CODE)

    print("\n======================")
    print("CANJE:", ok)
    print("RESULTADO:", reason)
    print("======================")

except MuseError as e:
    print("\nERROR DE MUSE:", e)

except SystemExit:
    raise

except Exception as e:
    print("\nERROR:", e)

finally:
    c.close()