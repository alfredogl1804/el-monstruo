#!/usr/bin/env python3.11
"""
create_skill.py — Entrypoint oficial de skill-factory.

Orquesta todo el pipeline de creación de skills:
1. Intake: captura y estructura la especificación
2. Classify: determina complejidad y template
3. Research: investiga el dominio (si aplica)
4. Architecture: diseña la arquitectura
5. Build: crea estructura de directorios
6. Generate: genera scripts y referencias
7. Generate SKILL.md: genera la documentación
8. Validate: valida estructura y calidad
9. Score: produce score final y veredicto

Uso:
    python3.11 create_skill.py --input "Descripción de la skill" --target /home/ubuntu/skills/
    python3.11 create_skill.py --input /path/to/description.md --target /home/ubuntu/skills/
    python3.11 create_skill.py --input desc.md --target /home/ubuntu/skills/ --skip-research
    python3.11 create_skill.py --input desc.md --target /home/ubuntu/skills/ --consult-sabios
"""

import argparse, asyncio, json, os, sys, yaml, time
from pathlib import Path
from datetime import datetime

# Add factory scripts to path
FACTORY_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(FACTORY_ROOT / "scripts"))
sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")

import intake_spec
import classify_complexity
import benchmark_before_build
import research_domain
import derive_architecture
import build_skill
import generate_scripts
import generate_references
import generate_skill_md
import validate_structure
import validate_quality
import score_skill


class SkillFactory:
    """Orquestador del pipeline de creación de skills."""
    
    def __init__(self, target_base: str, skip_research: bool = False,
                 consult_sabios: bool = False, depth: str = "normal",
                 skip_benchmark: bool = False, force_build: bool = False):
        self.target_base = Path(target_base)
        self.skip_research = skip_research
        self.consult_sabios = consult_sabios
        self.depth = depth
        self.skip_benchmark = skip_benchmark
        self.force_build = force_build
        self.workspace = None
        self.start_time = None
        self.log = []
    
    def _log(self, step: str, msg: str):
        elapsed = time.time() - self.start_time if self.start_time else 0
        entry = f"[{elapsed:6.1f}s] [{step}] {msg}"
        self.log.append(entry)
        print(entry)
    
    async def run(self, description: str) -> dict:
        """Ejecuta el pipeline completo."""
        self.start_time = time.time()
        
        self._log("INIT", "Iniciando skill-factory pipeline")
        
        # === PASO 1: INTAKE ===
        self._log("INTAKE", "Capturando especificación...")
        spec = await intake_spec.generate_spec(description)
        spec = intake_spec.enrich_spec(spec)
        
        skill_name = spec.get("name", "unnamed-skill")
        self._log("INTAKE", f"Skill: {skill_name} ({spec.get('domain')})")
        
        # Crear workspace temporal
        self.workspace = Path(f"/tmp/skill-factory/{skill_name}")
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Guardar spec
        spec_path = self.workspace / "spec.yaml"
        with open(spec_path, 'w', encoding='utf-8') as f:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # === PASO 2: CLASSIFY ===
        self._log("CLASSIFY", "Clasificando complejidad...")
        classification = classify_complexity.classify(spec)
        
        class_path = self.workspace / "classification.yaml"
        with open(class_path, 'w', encoding='utf-8') as f:
            yaml.dump(classification, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        level = classification.get("complexity_level", "standard")
        score = classification.get("complexity_score", 0)
        self._log("CLASSIFY", f"Nivel: {level} (score: {score}/10)")
        
        # === PASO 2.5: BENCHMARK BEFORE BUILD (NUEVO v2.0) ===
        benchmark_report = None
        if self.skip_benchmark:
            self._log("BENCHMARK", "Saltando benchmark (--skip-benchmark)")
        else:
            self._log("BENCHMARK", "Ejecutando Gap Analysis + Benchmark...")
            try:
                benchmark_report = await benchmark_before_build.run_benchmark(spec, deep_scout=False)
                
                bench_path = self.workspace / "benchmark_report.yaml"
                with open(bench_path, 'w', encoding='utf-8') as f:
                    yaml.dump(benchmark_report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                action = benchmark_report.get("decision", {}).get("action", "build")
                confidence = benchmark_report.get("decision", {}).get("confidence", 0)
                internal_pct = benchmark_report.get("internal_analysis", {}).get("internal_coverage_pct", 0)
                
                self._log("BENCHMARK", f"Decisión: {action.upper()} (confianza: {confidence*100:.0f}%, cobertura interna: {internal_pct}%)")
                
                # Si la decisión NO es build y no se forzó, informar y sugerir alternativa
                if action != "build" and not self.force_build:
                    reasoning = benchmark_report.get("decision", {}).get("reasoning", [])
                    for r in reasoning:
                        self._log("BENCHMARK", f"  → {r}")
                    
                    if action == "install":
                        target = benchmark_report.get("decision", {}).get("target", "?")
                        self._log("BENCHMARK", f"RECOMENDACIÓN: Instalar desde {target} en vez de construir")
                        self._log("BENCHMARK", "Usa --force-build para ignorar y construir de todas formas")
                    elif action == "extend_existing":
                        target = benchmark_report.get("decision", {}).get("target", "?")
                        self._log("BENCHMARK", f"RECOMENDACIÓN: Extender skill existente en {target}")
                    elif action == "compose":
                        composable = benchmark_report.get("decision", {}).get("composable_from", [])
                        self._log("BENCHMARK", f"RECOMENDACIÓN: Componer desde capabilities existentes: {composable}")
                    elif action == "fork_and_harden":
                        target = benchmark_report.get("decision", {}).get("target", "?")
                        self._log("BENCHMARK", f"RECOMENDACIÓN: Fork y endurecer desde {target}")
                    
                    # No detener el pipeline, pero registrar la recomendación
                    self._log("BENCHMARK", "Continuando con build por defecto...")
                else:
                    self._log("BENCHMARK", "Procediendo con build")
            except Exception as e:
                self._log("BENCHMARK", f"Error en benchmark (no bloquea): {e}")
        
        # === PASO 3: RESEARCH (si aplica) ===
        dossier_path = self.workspace / "dossier.md"
        
        if self.skip_research:
            self._log("RESEARCH", "Saltando investigación (--skip-research)")
            dossier_path.write_text("# Sin investigación\n\nInvestigación omitida por usuario.", encoding="utf-8")
        elif level == "minimal" and not spec.get("needs_realtime_research"):
            self._log("RESEARCH", "Skill minimal — investigación no requerida")
            dossier_path.write_text("# Investigación no requerida\n\nSkill de complejidad minimal.", encoding="utf-8")
        else:
            self._log("RESEARCH", f"Investigando dominio (profundidad: {self.depth})...")
            try:
                topics = await research_domain.identify_research_topics(spec, self.depth)
                self._log("RESEARCH", f"{len(topics)} temas identificados")
                
                semaphore = asyncio.Semaphore(4)
                tasks = [research_domain.research_topic(t, semaphore) for t in topics]
                results = await asyncio.gather(*tasks)
                
                ok = sum(1 for r in results if r["status"] == "ok")
                self._log("RESEARCH", f"{ok}/{len(results)} temas investigados")
                
                existing = await research_domain.check_existing_skills(spec)
                dossier = research_domain.compile_dossier(spec, topics, results, existing)
                dossier_path.write_text(dossier, encoding="utf-8")
                self._log("RESEARCH", f"Dossier: {len(dossier):,} chars")
            except Exception as e:
                self._log("RESEARCH", f"Error en investigación: {e}")
                dossier_path.write_text(f"# Error en investigación\n\n{e}", encoding="utf-8")
        
        # === PASO 3.5: CONSULT SABIOS (si se requiere) ===
        if self.consult_sabios or spec.get("needs_sabios_consultation"):
            self._log("SABIOS", "Consultando a los sabios para diseño...")
            try:
                sabios_output = self.workspace / "sabios_output"
                sabios_output.mkdir(exist_ok=True)
                
                # Preparar prompt para los sabios
                sabios_prompt = self.workspace / "sabios_prompt.md"
                sabios_prompt.write_text(
                    f"# Consulta de Diseño para Skill: {skill_name}\n\n"
                    f"## Especificación\n```yaml\n{yaml.dump(spec, default_flow_style=False, allow_unicode=True)}\n```\n\n"
                    f"## Clasificación\n```yaml\n{yaml.dump(classification, default_flow_style=False, allow_unicode=True)}\n```\n\n"
                    f"## Dossier\n{dossier_path.read_text(encoding='utf-8')[:10000]}\n\n"
                    f"Diseña la mejor arquitectura posible para esta skill. Incluye scripts, referencias, flujo de ejecución y quality gates.",
                    encoding="utf-8"
                )
                
                import subprocess
                result = subprocess.run(
                    ["python3.11", "/home/ubuntu/skills/consulta-sabios/scripts/run_consulta_sabios.py",
                     "--prompt", str(sabios_prompt),
                     "--output-dir", str(sabios_output),
                     "--modo", "enjambre",
                     "--profundidad-pre", "rapida"],
                    capture_output=True, text=True, timeout=600,
                    cwd="/home/ubuntu/skills/consulta-sabios/scripts"
                )
                
                if result.returncode == 0:
                    self._log("SABIOS", "Consulta completada")
                else:
                    self._log("SABIOS", f"Error: {result.stderr[:200]}")
            except Exception as e:
                self._log("SABIOS", f"Error consultando sabios: {e}")
        
        # === PASO 4: ARCHITECTURE ===
        self._log("ARCH", "Diseñando arquitectura...")
        dossier_text = dossier_path.read_text(encoding="utf-8")
        architecture = await derive_architecture.design_architecture(spec, classification, dossier_text)
        
        arch_path = self.workspace / "architecture.yaml"
        with open(arch_path, 'w', encoding='utf-8') as f:
            yaml.dump(architecture, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        scripts_count = len(architecture.get("scripts_detail", []))
        self._log("ARCH", f"Arquitectura: {scripts_count} scripts, entrypoint: {architecture.get('entrypoint', 'N/A')}")
        
        # === PASO 5: BUILD STRUCTURE ===
        skill_dir = self.target_base / skill_name
        self._log("BUILD", f"Creando estructura en: {skill_dir}")
        build_skill.build_structure(architecture, skill_dir)
        
        # === PASO 6: GENERATE SCRIPTS ===
        self._log("GENERATE", f"Generando {scripts_count} scripts...")
        scripts_detail = architecture.get("scripts_detail", [])
        
        # Ordenar por prioridad
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        scripts_detail.sort(key=lambda s: priority_order.get(s.get("priority", "P1"), 1))
        
        generated_scripts = {}
        for i, sd in enumerate(scripts_detail):
            filename = sd.get("filename", f"script_{i}.py")
            self._log("GENERATE", f"  [{i+1}/{len(scripts_detail)}] {filename}...")
            try:
                code = await generate_scripts.generate_single_script(
                    sd, spec, architecture, dossier_text, generated_scripts
                )
                issues = generate_scripts.validate_script(code, filename)
                critical = [x for x in issues if "CRITICAL" in x]
                
                if critical:
                    self._log("GENERATE", f"    Reintentando {filename}...")
                    code = await generate_scripts.generate_single_script(
                        sd, spec, architecture, dossier_text, generated_scripts
                    )
                
                script_path = skill_dir / "scripts" / filename
                script_path.write_text(code, encoding="utf-8")
                generated_scripts[filename] = code
                self._log("GENERATE", f"    ✅ {filename}: {len(code.split(chr(10)))} líneas")
            except Exception as e:
                self._log("GENERATE", f"    ❌ {filename}: {e}")
        
        # === PASO 7: GENERATE REFERENCES ===
        refs_detail = architecture.get("references_detail", [])
        if refs_detail:
            self._log("REFS", f"Generando {len(refs_detail)} referencias...")
            for i, rd in enumerate(refs_detail):
                filename = rd.get("filename", f"ref_{i}.md")
                try:
                    content = await generate_references.generate_single_reference(rd, spec, dossier_text)
                    ref_path = skill_dir / "references" / filename
                    ref_path.parent.mkdir(parents=True, exist_ok=True)
                    ref_path.write_text(content, encoding="utf-8")
                    self._log("REFS", f"  ✅ {filename}")
                except Exception as e:
                    self._log("REFS", f"  ❌ {filename}: {e}")
        
        # === PASO 8: GENERATE SKILL.MD ===
        self._log("SKILLMD", "Generando SKILL.md...")
        skill_md_content = await generate_skill_md.generate_skill_md(spec, architecture)
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(skill_md_content, encoding="utf-8")
        self._log("SKILLMD", f"SKILL.md: {len(skill_md_content.split(chr(10)))} líneas")
        
        # === PASO 9: VALIDATE ===
        self._log("VALIDATE", "Validando estructura...")
        
        # Estructura
        struct_issues = []
        struct_issues.extend(validate_structure.validate_frontmatter(skill_md_path))
        struct_issues.extend(validate_structure.validate_directories(skill_dir))
        struct_issues.extend(validate_structure.validate_scripts(skill_dir))
        struct_issues.extend(validate_structure.validate_references(skill_dir, skill_md_content))
        struct_scores = validate_structure.calculate_scores(struct_issues)
        
        struct_report = {"scores": struct_scores, "issues": struct_issues}
        struct_path = self.workspace / "structure_report.yaml"
        with open(struct_path, 'w', encoding='utf-8') as f:
            yaml.dump(struct_report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        self._log("VALIDATE", f"Estructura: {struct_scores['verdict']} ({struct_scores['score']}/100)")
        
        # Calidad (IA judge)
        self._log("VALIDATE", "Evaluando calidad con Claude...")
        try:
            skill_content = validate_quality.collect_skill_content(skill_dir)
            quality_eval = await validate_quality.evaluate_quality(skill_content, spec)
        except Exception as e:
            self._log("VALIDATE", f"Error en evaluación de calidad: {e}")
            quality_eval = {"global_score": 50, "grade": "Error", "dimensions": {},
                          "top_strengths": [], "top_weaknesses": [str(e)],
                          "critical_fixes": [], "improvement_suggestions": []}
        
        quality_path = self.workspace / "quality_report.yaml"
        with open(quality_path, 'w', encoding='utf-8') as f:
            yaml.dump(quality_eval, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        self._log("VALIDATE", f"Calidad: {quality_eval.get('grade', 'N/A')} ({quality_eval.get('global_score', 0)}/100)")
        
        # === PASO 10: SCORE FINAL ===
        final = score_skill.calculate_final_score(struct_report, quality_eval)
        
        final_path = self.workspace / "final_score.yaml"
        with open(final_path, 'w', encoding='utf-8') as f:
            yaml.dump(final, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        elapsed = time.time() - self.start_time
        
        self._log("DONE", f"Pipeline completado en {elapsed:.0f}s")
        self._log("DONE", f"SCORE: {final['final_score']}/100 — {final['verdict']}")
        self._log("DONE", f"Skill en: {skill_dir}")
        
        # Guardar log
        log_path = self.workspace / "pipeline_log.txt"
        log_path.write_text("\n".join(self.log), encoding="utf-8")
        
        return {
            "skill_name": skill_name,
            "skill_dir": str(skill_dir),
            "workspace": str(self.workspace),
            "final_score": final["final_score"],
            "verdict": final["verdict"],
            "action": final["action"],
            "deliverable": final["deliverable"],
            "elapsed_seconds": round(elapsed, 1),
            "scripts_generated": len(generated_scripts),
            "scripts_planned": scripts_count
        }


async def main():
    parser = argparse.ArgumentParser(
        description="skill-factory: Crea skills de primer nivel de cualquier dominio"
    )
    parser.add_argument("--input", required=True,
                       help="Descripción de la skill (texto directo o path a archivo .md)")
    parser.add_argument("--target", default="/home/ubuntu/skills",
                       help="Directorio base donde crear la skill (default: /home/ubuntu/skills)")
    parser.add_argument("--skip-research", action="store_true",
                       help="Saltar investigación de dominio")
    parser.add_argument("--consult-sabios", action="store_true",
                       help="Consultar a los 6 sabios para el diseño")
    parser.add_argument("--depth", default="normal", choices=["basic", "normal", "deep"],
                       help="Profundidad de investigación")
    parser.add_argument("--skip-benchmark", action="store_true",
                       help="Saltar benchmark before build")
    parser.add_argument("--force-build", action="store_true",
                       help="Forzar build incluso si benchmark recomienda otra acción")
    args = parser.parse_args()
    
    # Leer input
    input_path = Path(args.input)
    if input_path.exists():
        description = input_path.read_text(encoding="utf-8")
    else:
        description = args.input
    
    # Ejecutar pipeline
    factory = SkillFactory(
        target_base=args.target,
        skip_research=args.skip_research,
        consult_sabios=args.consult_sabios,
        depth=args.depth,
        skip_benchmark=args.skip_benchmark,
        force_build=args.force_build
    )
    
    result = await factory.run(description)
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"  SKILL-FACTORY — RESULTADO FINAL")
    print(f"{'='*60}")
    print(f"  Skill: {result['skill_name']}")
    print(f"  Score: {result['final_score']}/100")
    print(f"  Veredicto: {result['verdict']}")
    print(f"  Entregable: {'Sí' if result['deliverable'] else 'No'}")
    print(f"  Scripts: {result['scripts_generated']}/{result['scripts_planned']}")
    print(f"  Tiempo: {result['elapsed_seconds']}s")
    print(f"  Skill en: {result['skill_dir']}")
    print(f"  Workspace: {result['workspace']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
