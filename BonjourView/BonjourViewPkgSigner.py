"""Signs a flat package with a Developer ID Installer identity using productsign."""

import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["BonjourViewPkgSigner"]


class BonjourViewPkgSigner(Processor):
    description = "Signs pkg_path in place with productsign. Skips packages that are already signed."
    input_variables = {
        "pkg_path": {"required": True, "description": "Path to the flat package to sign."},
        "signing_identity": {
            "required": False,
            "description": "Optional. Name of a Developer ID Installer identity in the keychain.",
        },
    }
    output_variables = {"pkg_path": {"description": "Path to the signed package."}}

    def main(self):
        pkg_path = self.env["pkg_path"]
        if not self.env.get("signing_identity"):
            self.output("No signing identity set; leaving package unsigned")
            return
        check = subprocess.run(
            ["/usr/sbin/pkgutil", "--check-signature", pkg_path], capture_output=True, text=True
        )
        if "Status: signed" in check.stdout:
            self.output(f"{pkg_path} is already signed")
            return
        unsigned = pkg_path + ".unsigned"
        os.rename(pkg_path, unsigned)
        result = subprocess.run(
            ["/usr/bin/productsign", "--sign", self.env["signing_identity"], "--timestamp", unsigned, pkg_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            os.rename(unsigned, pkg_path)
            raise ProcessorError(f"productsign failed: {result.stderr.strip()}")
        os.remove(unsigned)
        self.output(f"Signed {pkg_path}")


if __name__ == "__main__":
    BonjourViewPkgSigner().execute_shell()
