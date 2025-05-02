# Dockerfile Security Best Practices

- **Minimize base images**  
  Use slim or distroless, e.g. `python:3.11-slim` or Chainguard images.

- **Don’t run as root**  
  Add a non-root user in your Dockerfile (e.g. `USER 1001`).

- **Avoid ad-hoc downloads**  
  Prefer package managers (e.g. `apt`) or `COPY` over `curl`/`wget`.

- **Pin versions**  
  Always specify exact versions for packages and dependencies.

- **Use multi-stage builds**  
  Strip out build‐time tools (compilers, curl, git) from your final image.

- **Validate artifacts**  
  When downloading from the web, verify checksums before installing.

- **Limit layers & artifacts**  
  Clean up caches (`rm -rf /var/lib/apt/lists/*`) and remove unneeded files.

- **Explicit permissions**  
  Set `COPY --chmod=…` or `RUN chmod` to tighten file access.

- **Beware of ADD**  
  Use `COPY` unless you really need `ADD`’s tar extraction.

- **Set HEALTHCHECK**  
  Give each container a meaningful `HEALTHCHECK` to detect failures.
