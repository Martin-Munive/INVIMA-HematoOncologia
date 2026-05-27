import React from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, BadgeCheck, ChevronDown, Database, FileSearch, FlaskConical, Search, ShieldCheck } from 'lucide-react';
import './styles.css';
import indicationPatternConfig from './indicationPatterns.json';

type ErrorBoundaryState = {
  hasError: boolean;
  message: string;
};

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, message: error.message };
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="app-shell">
        <main className="workspace">
          <section className="fallback-panel">
            <AlertTriangle size={22} />
            <div>
              <strong>No se pudo renderizar la ficha</strong>
              <p>Recarga la pagina o vuelve a consultar el medicamento. Detalle tecnico: {this.state.message || 'error no especificado'}.</p>
            </div>
          </section>
        </main>
      </div>
    );
  }
}

type Completion = {
  is_complete_for_current_sources: boolean;
  missing_sources: string[];
};

type ManualProfile = {
  nombre: string;
  mecanismo: string;
  efectos_adversos: string;
  extravasacion: string;
  indicacion_manual: string;
} | null;

type InvimaDetail = {
  expediente: string;
  cdgprod: string;
  producto: string;
  registro_sanitario: string;
  estado: string;
  forma_farmaceutica: string;
  principio_activo: string;
  concentracion: string;
  atc: string;
  indicaciones: string;
  source_label?: string;
  source_url?: string;
  source_reference?: string;
};

type UnirsItem = {
  principio_activo: string;
  dci_concentracion: string;
  forma_farmaceutica: string;
  indicaciones: string;
  tipo_indicacion: string;
  indicacion_habilitada: string;
};

type PosPopuliItem = {
  nombre: string;
  tipo: string;
  codigo_atc: string;
  descripcion: string;
  detalle_url: string;
  financiacion: string;
};

type ClinicalSafety = {
  drug: string;
  source_status: string;
  definition?: string;
  mechanism?: string;
  mechanism_sources?: { label: string; url: string }[];
  sources: { label: string; url: string }[];
  adverse_reactions_by_system: { system: string; items: string[] }[];
  common_adverse_reactions?: { reaction: string; frequency: string; source?: string }[];
  hypersensitivity: {
    risk: string;
    prevention: string[];
    management: string[];
  };
  extravasation: {
    classification: string;
    prevention: string[];
    management: string[];
  };
} | null;

type DrugReport = {
  query: string;
  only_vigente: boolean;
  completion: Completion;
  manual_profile: ManualProfile;
  invima: {
    registration_counts: { estado: string; n: number }[];
    details_count: number;
    details: InvimaDetail[];
    curated_indications?: CuratedIndications;
  };
  unirs: { count: number; items: UnirsItem[] };
  pospopuli: { count: number; items: PosPopuliItem[]; status?: PosStatus };
  manual_summary_status?: SectionStatus;
  clinical_safety: ClinicalSafety;
  clinical_safety_status?: SectionStatus;
  source_policy: Record<string, string>;
};

type DrugSuggestion = {
  name: string;
  sources: string[];
  count: number;
};

type SectionStatus = {
  data_status: string;
  needs_curation: boolean;
  reason?: string;
  missing_fields?: string[];
};

type CuratedIndication = {
  condition: string;
  condition_normalized: string;
  scenario: string;
  population: string;
  line_of_therapy: string;
  combination: string;
  transplant_context: string;
  evidence_span: string;
  scenarios?: string[];
  evidence_spans?: string[];
  confidence: string;
  review_status: string;
  presentations: {
    expediente: string;
    producto: string;
    registro_sanitario: string;
  }[];
};

type CuratedIndications = {
  data_status: string;
  curation_status: string;
  count: number;
  items: CuratedIndication[];
};

type PosStatus = {
  acquisition_status: string;
  found: boolean | null;
  ui_safe_to_conclude_absence: boolean;
  message_for_ui: string;
  items: PosPopuliItem[];
  query_term?: string;
  last_checked_at?: string;
  evidence_url?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? '';

type RegulatoryIndicationSummary = {
  label: string;
  presentations: {
    producto: string;
    registro_sanitario: string;
    concentracion: string;
    forma_farmaceutica: string;
  }[];
};

type UnirsIndicationSummary = {
  label: string;
  items: {
    dci_concentracion: string;
    forma_farmaceutica: string;
    tipo_indicacion: string;
    indicaciones: string;
  }[];
};

type IndicationPatternDefinition = { label: string; pattern: string };

function compilePatterns(items: IndicationPatternDefinition[]) {
  return items.map((item) => ({ label: item.label, pattern: new RegExp(item.pattern, 'i') }));
}

const INDICATION_PATTERNS = compilePatterns(indicationPatternConfig.invima);
function statusClass(ok: boolean) {
  return ok ? 'status-ok' : 'status-warn';
}

function splitBullets(text: string) {
  return text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function normalizeSearchText(text: string) {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase();
}

function normalizeGroupKey(text: string) {
  return normalizeSearchText(text).replace(/\s+/g, ' ').trim();
}

function formatIndicationText(text: string) {
  const compact = text.replace(/\s+/g, ' ').trim();
  if (!compact) return '';
  const upperLetters = compact.match(/[A-ZÁÉÍÓÚÑ]/g)?.length ?? 0;
  const lowerLetters = compact.match(/[a-záéíóúñ]/g)?.length ?? 0;
  if (upperLetters <= lowerLetters * 2) return compact;

  const lowered = compact.toLocaleLowerCase('es-CO');
  return lowered
    .replace(/(^|[.!?]\s+)([a-záéíóúñ])/g, (_match, prefix: string, letter: string) => `${prefix}${letter.toLocaleUpperCase('es-CO')}`)
    .replace(/\b(invima|unirs|pos|upc|atc|vih|her2|egfr|alk|ros1|pd-1|pd-l1|ctla-4|braf|ras)\b/gi, (match) => match.toUpperCase());
}

function cleanNumber(value: string) {
  if (!value) return '';
  return value.replace(',', '.').replace(/\.?0+$/, '');
}

function displayConcentration(presentation: { producto: string; concentracion: string; forma_farmaceutica: string }) {
  const productText = presentation.producto.replace(/\s+/g, ' ').trim();
  const match = productText.match(/\b\d+(?:[.,]\d+)?\s*(?:MG|MCG|G|UI|U)(?:\s*\/\s*\d+(?:[.,]\d+)?\s*(?:ML|L|U))?/i);
  if (match) return match[0].toUpperCase();
  const numeric = cleanNumber(presentation.concentracion);
  if (numeric) return `${numeric} (campo INVIMA)`;
  return presentation.forma_farmaceutica || 'Sin dato';
}

function buildRegulatorySummary(details: InvimaDetail[]) {
  const grouped = new Map<string, RegulatoryIndicationSummary>();

  details.forEach((detail) => {
    const indicationText = normalizeSearchText(detail.indicaciones || '');
    INDICATION_PATTERNS.forEach(({ label, pattern }) => {
      if (!pattern.test(indicationText)) return;
      const current = grouped.get(label) ?? { label, presentations: [] };
      const alreadyListed = current.presentations.some(
        (presentation) => presentation.registro_sanitario === detail.registro_sanitario && presentation.producto === detail.producto,
      );
      if (!alreadyListed) {
        current.presentations.push({
          producto: detail.producto,
          registro_sanitario: detail.registro_sanitario,
          concentracion: detail.concentracion,
          forma_farmaceutica: detail.forma_farmaceutica,
        });
      }
      grouped.set(label, current);
    });
  });

  return Array.from(grouped.values()).sort((a, b) => b.presentations.length - a.presentations.length || a.label.localeCompare(b.label));
}

function buildUnirsSummary(items: UnirsItem[]) {
  const grouped = new Map<string, UnirsIndicationSummary>();

  items.forEach((item) => {
    const rawIndication = item.indicaciones?.replace(/\s+/g, ' ').trim();
    if (!rawIndication) return;
    const key = normalizeGroupKey(rawIndication);
    const label = formatIndicationText(rawIndication);
    const current = grouped.get(key) ?? { label, items: [] };
    const alreadyListed = current.items.some(
      (entry) =>
        entry.dci_concentracion === item.dci_concentracion
        && entry.tipo_indicacion === item.tipo_indicacion
        && entry.forma_farmaceutica === item.forma_farmaceutica,
    );
    if (!alreadyListed) {
      current.items.push({
        dci_concentracion: item.dci_concentracion,
        forma_farmaceutica: item.forma_farmaceutica,
        tipo_indicacion: item.tipo_indicacion || 'Sin clasificacion',
        indicaciones: rawIndication,
      });
    }
    grouped.set(key, current);
  });

  return Array.from(grouped.values()).sort((a, b) => b.items.length - a.items.length || a.label.localeCompare(b.label));
}

function Panel({ title, icon, children, className = '' }: { title: string; icon: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={`hud-panel ${className}`}>
      <div className="panel-title">
        {icon}
        <span>{title}</span>
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

function normalizeReport(raw: DrugReport): DrugReport {
  return {
    ...raw,
    completion: {
      is_complete_for_current_sources: raw.completion?.is_complete_for_current_sources ?? false,
      missing_sources: raw.completion?.missing_sources ?? [],
    },
    invima: {
      registration_counts: raw.invima?.registration_counts ?? [],
      details_count: raw.invima?.details_count ?? 0,
      details: raw.invima?.details ?? [],
      curated_indications: raw.invima?.curated_indications ?? { data_status: 'none', curation_status: 'none', count: 0, items: [] },
    },
    unirs: {
      count: raw.unirs?.count ?? 0,
      items: raw.unirs?.items ?? [],
    },
    pospopuli: {
      count: raw.pospopuli?.count ?? 0,
      items: raw.pospopuli?.items ?? [],
      status: raw.pospopuli?.status ?? {
        acquisition_status: 'not_loaded',
        found: null,
        ui_safe_to_conclude_absence: false,
        message_for_ui: 'POS Populi pendiente de consulta local; no afirmar ausencia de financiacion.',
        items: [],
      },
    },
    manual_summary_status: raw.manual_summary_status ?? { data_status: 'none', needs_curation: true },
    clinical_safety_status: raw.clinical_safety_status ?? { data_status: raw.clinical_safety ? 'candidate' : 'missing_source', needs_curation: !raw.clinical_safety },
    source_policy: raw.source_policy ?? {},
  };
}

function selectedDrugName(report: DrugReport) {
  return (
    report.manual_profile?.nombre ||
    report.invima.details[0]?.principio_activo ||
    report.unirs.items[0]?.principio_activo ||
    report.query
  );
}

function localDrugDescription(report: DrugReport) {
  if (report.clinical_safety?.definition && report.clinical_safety?.mechanism) {
    return `${report.clinical_safety.definition} ${report.clinical_safety.mechanism}`;
  }
  if (report.manual_profile?.mecanismo) return report.manual_profile.mecanismo;
  if (report.clinical_safety) return 'Perfil clinico verificado disponible para seguridad, hipersensibilidad y manejo de extravasacion.';
  return 'Ficha consolidada local con detalles INVIMA, UNIRS, POS Populi y perfil clinico disponible para el medicamento seleccionado.';
}

function DrugHeader({ report, financed }: { report: DrugReport; financed: boolean }) {
  const firstDetail = report.invima.details[0];
  const title = selectedDrugName(report);
  const posNames = report.pospopuli.items.map((item) => item.nombre).join(', ');
  return (
    <section className="drug-header">
      <div className="drug-title-block">
        <span className="eyebrow">Medicamento seleccionado</span>
        <h1>{title}</h1>
        <p>{localDrugDescription(report)}</p>
      </div>
      <div className="drug-facts">
        <div>
          <span>UPC / POS Populi</span>
          <strong>{financed ? 'Financiado' : report.pospopuli.status?.acquisition_status === 'not_found' ? 'No encontrado' : 'Pendiente'}</strong>
          {posNames && <small>{posNames}</small>}
          {!posNames && <small>{report.pospopuli.status?.message_for_ui}</small>}
        </div>
        <div>
          <span>ATC</span>
          <strong>{firstDetail?.atc || 'Sin dato'}</strong>
          <small>{firstDetail?.forma_farmaceutica || 'Detalle INVIMA'}</small>
        </div>
        <div>
          <span>Presentaciones INVIMA</span>
          <strong>{report.invima.details_count}</strong>
          <small>Registros vigentes con texto regulatorio</small>
        </div>
        <div>
          <span>Registros UNIRS</span>
          <strong>{report.unirs.count}</strong>
          <small>Registros complementarios</small>
        </div>
      </div>
    </section>
  );
}

function EmptyDashboard() {
  return (
    <section className="empty-dashboard">
      <div className="empty-report-slot">
        <FileSearch size={18} />
        <span>Resumen regulatorio pendiente</span>
      </div>
      <div className="empty-report-slot">
        <ShieldCheck size={18} />
        <span>Indicaciones y presentaciones pendientes</span>
      </div>
      <div className="empty-report-slot">
        <AlertTriangle size={18} />
        <span>Seguridad clinica pendiente</span>
      </div>
      <div className="empty-report-slot">
        <Database size={18} />
        <span>Fuentes pendientes</span>
      </div>
    </section>
  );
}

function App() {
  const [query, setQuery] = React.useState('');
  const [report, setReport] = React.useState<DrugReport | null>(null);
  const [suggestions, setSuggestions] = React.useState<DrugSuggestion[]>([]);
  const [suggestionIndex, setSuggestionIndex] = React.useState(0);
  const [suggestionsOpen, setSuggestionsOpen] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const selectedSuggestionRef = React.useRef('');

  const loadReport = React.useCallback(async (termOverride?: string) => {
    const term = (termOverride ?? query).trim();
    if (!term) return;
    setQuery(term);
    selectedSuggestionRef.current = term;
    setSuggestions([]);
    setSuggestionsOpen(false);
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/drugs/${encodeURIComponent(term)}/report?only_vigente=true`);
      if (!response.ok) {
        throw new Error(`API ${response.status}`);
      }
      const payload = await response.json();
      setReport(normalizeReport(payload));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo consultar la API local');
    } finally {
      setLoading(false);
    }
  }, [query]);

  React.useEffect(() => {
    const term = query.trim();
    if (term === selectedSuggestionRef.current) {
      setSuggestions([]);
      setSuggestionsOpen(false);
      return;
    }
    if (term.length < 2) {
      setSuggestions([]);
      setSuggestionsOpen(false);
      return;
    }
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch(`${API_BASE}/api/drugs/suggest?q=${encodeURIComponent(term)}&limit=10`, { signal: controller.signal });
        if (!response.ok) return;
        const payload = await response.json();
        setSuggestions(payload.items ?? []);
        setSuggestionIndex(0);
        setSuggestionsOpen(Boolean(payload.items?.length));
      } catch (err) {
        if (!(err instanceof DOMException && err.name === 'AbortError')) {
          setSuggestions([]);
          setSuggestionsOpen(false);
        }
      }
    }, 160);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [query]);

  function handleSearchKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowDown' && suggestions.length) {
      event.preventDefault();
      setSuggestionIndex((current) => Math.min(current + 1, suggestions.length - 1));
      setSuggestionsOpen(true);
      return;
    }
    if (event.key === 'ArrowUp' && suggestions.length) {
      event.preventDefault();
      setSuggestionIndex((current) => Math.max(current - 1, 0));
      setSuggestionsOpen(true);
      return;
    }
    if (event.key === 'Tab' && suggestionsOpen && suggestions[0]) {
      event.preventDefault();
      setQuery(suggestions[0].name);
      setSuggestionsOpen(false);
      return;
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      loadReport(suggestionsOpen && suggestions[suggestionIndex] ? suggestions[suggestionIndex].name : query);
    }
  }

  const financed = Boolean(report?.pospopuli.items.some((item) => item.financiacion));
  const complete = Boolean(report?.completion.is_complete_for_current_sources);
  const curatedIndications = report?.invima.curated_indications?.items ?? [];
  const unirsSummary = report ? buildUnirsSummary(report.unirs.items) : [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <Activity size={24} />
          <div>
            <div className="brand-title">INVIMA HEMATO-ONCOLOGIA</div>
            <div className="brand-subtitle">Centro local de consulta regulatoria y farmacologica</div>
          </div>
        </div>
        <div className="system-strip">
          <strong>Martin Munive</strong>
          <span>Medico General</span>
          <span>Analista y programador de software</span>
        </div>
      </header>

      <main className="workspace">
        <section className="search-band">
          <div className="search-wrap">
            <div className="search-box">
              <Search size={18} />
              <input
                value={query}
                placeholder="Buscar medicamento por principio activo"
                onBlur={() => window.setTimeout(() => setSuggestionsOpen(false), 140)}
                onChange={(event) => {
                  setQuery(event.target.value);
                  selectedSuggestionRef.current = '';
                  setReport(null);
                }}
                onFocus={() => setSuggestionsOpen(Boolean(suggestions.length))}
                onKeyDown={handleSearchKeyDown}
              />
              <button onClick={() => loadReport()} disabled={loading || !query.trim()}>{loading ? 'Consultando' : 'Buscar'}</button>
            </div>
            {suggestionsOpen && (
              <div className="suggestion-list">
                {suggestions.map((item, index) => (
                  <button
                    className={index === suggestionIndex ? 'suggestion active' : 'suggestion'}
                    key={item.name}
                    onPointerDown={(event) => {
                      event.preventDefault();
                      selectedSuggestionRef.current = item.name;
                      setSuggestions([]);
                      setSuggestionsOpen(false);
                      loadReport(item.name);
                    }}
                    type="button"
                  >
                    <strong>{item.name}</strong>
                    <span>{item.sources.join(' · ')} · {item.count} registros fuente consolidados</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          {error && <div className="error-line"><AlertTriangle size={16} /> {error}</div>}
        </section>

        {loading && !report && (
          <section className="fallback-panel">
            <Database size={22} />
            <div>
              <strong>Consultando base local</strong>
              <p>La API esta construyendo el reporte consolidado del medicamento.</p>
            </div>
          </section>
        )}

        {!loading && !report && <EmptyDashboard />}

        {report && (
          <>
            <DrugHeader report={report} financed={financed} />
            <section className="summary-grid">
              <div className={`metric ${statusClass(complete)}`}>
                <BadgeCheck size={22} />
                <span>Completitud</span>
                <strong>{complete ? 'Completo' : 'Incompleto'}</strong>
              </div>
              <div className={`metric ${statusClass(financed)}`}>
                <ShieldCheck size={22} />
                <span>UPC / Estado</span>
                <strong>{financed ? 'Financiado' : report?.pospopuli.status?.acquisition_status === 'not_found' ? 'No encontrado' : 'Pendiente'}</strong>
              </div>
              <div className="metric">
                <Database size={22} />
                <span>Presentaciones INVIMA</span>
                <strong>{report.invima.details_count}</strong>
              </div>
              <div className="metric">
                <FlaskConical size={22} />
                <span>Registros UNIRS</span>
                <strong>{report.unirs.count}</strong>
              </div>
            </section>

            <section className="content-grid">
              <Panel title="Resumen regulatorio" icon={<FileSearch size={16} />} className="regulatory-panel">
                <div className="count-row">
                  {report.invima.registration_counts.map((item) => (
                    <span key={item.estado} className="count-chip">{item.estado}: {item.n}</span>
                  ))}
                </div>
                <div className="subsection-title">Indicaciones INVIMA vigentes</div>
                <div className="source-note">
                  Esta vista agrupa indicaciones verificadas con evidencia textual. El texto bruto queda abajo como soporte de consulta, no como clasificacion automatica.
                </div>
                {curatedIndications.length ? (
                  <div className="regulatory-summary">
                    {curatedIndications.map((item) => (
                      <details key={`${item.condition_normalized}-${item.scenario}-${item.evidence_span}`} className="indication-summary-section">
                        <summary className="indication-summary-head">
                          <ChevronDown size={16} aria-hidden="true" />
                          <strong>{item.condition_normalized}</strong>
                          <span>{item.presentations.length} presentaciones</span>
                          <small>Abrir</small>
                        </summary>
                        {(item.scenarios?.length ? item.scenarios : [item.scenario]).filter(Boolean).map((scenario) => (
                          <p className="source-note" key={`${item.condition_normalized}-${scenario}`}>{scenario}</p>
                        ))}
                        {item.combination && <p className="source-note">Combinacion/contexto: {item.combination}</p>}
                        <div className="presentation-list">
                          <div className="presentation-list-head">
                            <span>Producto</span>
                            <span>Expediente</span>
                            <span>Registro</span>
                          </div>
                          {item.presentations.map((presentation) => (
                            <div className="presentation-line" key={`${item.condition_normalized}-${item.scenario}-${presentation.producto}-${presentation.registro_sanitario}`}>
                              <span>{presentation.producto}</span>
                              <span>{presentation.expediente}</span>
                              <span>{presentation.registro_sanitario}</span>
                            </div>
                          ))}
                        </div>
                        <div className="source-note">
                          Evidencia textual: {(item.evidence_spans?.length ? item.evidence_spans : [item.evidence_span]).filter(Boolean).join('; ')}
                        </div>
                      </details>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="Indicaciones INVIMA pendientes de verificacion. No se publican patologias inferidas por regex." />
                )}
                <div className="subsection-title">Indicaciones UNIRS vigentes</div>
                {unirsSummary.length ? (
                  <div className="unirs-summary-list">
                    {unirsSummary.map((item) => (
                      <details className="unirs-summary-section" key={item.label}>
                        <summary className="indication-summary-head">
                          <ChevronDown size={16} aria-hidden="true" />
                          <strong>{item.label}</strong>
                          <span>{item.items.length} registros UNIRS</span>
                          <small>Abrir</small>
                        </summary>
                        <div className="unirs-compact-list">
                          {item.items.map((entry) => (
                            <div className="unirs-compact-line" key={`${item.label}-${entry.dci_concentracion}-${entry.tipo_indicacion}`}>
                              <span>{entry.dci_concentracion}</span>
                              <span>{entry.forma_farmaceutica || 'Sin forma reportada'}</span>
                              <span>{entry.tipo_indicacion}</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="No hay indicaciones UNIRS locales para este medicamento." />
                )}
                <div className="source-note">Fuente: derivado del campo de indicaciones INVIMA por presentacion vigente, documento oficial INVIMA verificado o texto UNIRS vigente. Confirmar el texto completo en los paneles inferiores antes de autorizar uso.</div>
                {report.completion.missing_sources.length > 0 && (
                  <div className="warning-box">Faltan fuentes: {report.completion.missing_sources.join(', ')}</div>
                )}
              </Panel>

              {report.manual_profile?.indicacion_manual && (
                <Panel title="Indicaciones resumidas locales" icon={<FileSearch size={16} />} className="detail-panel local-summary-panel">
                  <div className="source-note">Fuente local de trabajo. Este bloque requiere curacion estructurada antes de usarse como soporte de autorizacion.</div>
                  {report.manual_summary_status?.needs_curation && (
                    <div className="warning-box">Resumen manual pendiente de curacion estructurada: {report.manual_summary_status.reason || report.manual_summary_status.data_status}</div>
                  )}
                  <details className="safety-group" open>
                    <summary><ChevronDown size={15} aria-hidden="true" /> <span>{report.manual_profile.nombre}</span><small>Abrir</small></summary>
                    {splitBullets(report.manual_profile.indicacion_manual).map((line) => <p key={line}>{line}</p>)}
                  </details>
                </Panel>
              )}

              <Panel title="Perfil clinico y seguridad" icon={<AlertTriangle size={16} />} className="clinical-panel">
                {report.clinical_safety || report.manual_profile ? (
                  <div className="safety-layout">
                    {report.clinical_safety_status?.needs_curation && (
                      <div className="warning-box">Seguridad clinica incompleta o pendiente de curacion: {(report.clinical_safety_status.missing_fields ?? []).join(', ') || report.clinical_safety_status.data_status}</div>
                    )}

                    {report.clinical_safety && (
                      <>

                    <div className="safety-column">
                      <div className="subsection-title">Reacciones adversas por sistema</div>
                      {report.clinical_safety.adverse_reactions_by_system.map((group) => (
                        <details className="safety-group" key={group.system}>
                          <summary><ChevronDown size={15} aria-hidden="true" /> <span>{group.system}</span><small>Abrir</small></summary>
                          <ul>
                            {group.items.map((item) => <li key={item}>{item}</li>)}
                          </ul>
                        </details>
                      ))}
                    </div>
                    <div className="safety-column">
                      {Boolean(report.clinical_safety.common_adverse_reactions?.length) && (
                        <>
                          <div className="subsection-title">Reacciones frecuentes</div>
                          <ul>
                            {report.clinical_safety.common_adverse_reactions?.map((item) => (
                              <li key={`${item.reaction}-${item.frequency}`}><strong>{item.reaction}:</strong> {item.frequency}</li>
                            ))}
                          </ul>
                        </>
                      )}
                      <div className="subsection-title">Hipersensibilidad / anafilaxia</div>
                      <p>{report.clinical_safety.hypersensitivity.risk}</p>
                      <ul>
                        {[...report.clinical_safety.hypersensitivity.prevention, ...report.clinical_safety.hypersensitivity.management].map((item) => <li key={item}>{item}</li>)}
                      </ul>
                      <div className="subsection-title">Extravasacion / infiltracion</div>
                      <p>{report.clinical_safety.extravasation.classification}</p>
                      <ul>
                        {[...report.clinical_safety.extravasation.prevention, ...report.clinical_safety.extravasation.management].map((item) => <li key={item}>{item}</li>)}
                      </ul>
                    </div>
                    <div className="source-note">
                      Fuentes verificadas: {[...(report.clinical_safety.mechanism_sources ?? []), ...report.clinical_safety.sources].map((source) => source.label).join('; ')}.
                    </div>
                      </>
                    )}
                    {!report.clinical_safety && report.manual_profile && (
                      <div className="source-note">Este medicamento solo tiene perfil manual local. Falta revision cientifica verificada para seguridad por sistema, hipersensibilidad y extravasacion.</div>
                    )}
                  </div>
                ) : <EmptyState text="Sin perfil clinico local ni revision cientifica verificada para este medicamento." />}
              </Panel>

              <Panel title="Indicaciones INVIMA por presentacion" icon={<ShieldCheck size={16} />} className="detail-panel invima-original-panel">
                {report.invima.details.length ? (
                  <div className="table-list">
                    {report.invima.details.map((item) => (
                      <details key={`${item.expediente}-${item.cdgprod}`} className="detail-row">
                        <summary className="detail-head">
                          <ChevronDown size={15} aria-hidden="true" />
                          <strong>{item.producto}</strong>
                          <span>{item.registro_sanitario}</span>
                          <small>Abrir fuente</small>
                        </summary>
                        <div className="detail-meta">
                          <span>{item.forma_farmaceutica}</span>
                          <span>{item.principio_activo}</span>
                          <span>{item.concentracion}</span>
                        </div>
                        <p>{formatIndicationText(item.indicaciones)}</p>
                        {item.source_label && (
                          <div className="source-note">
                            Fuente: {item.source_url ? <a href={item.source_url} target="_blank" rel="noreferrer">{item.source_label}</a> : item.source_label}
                            {item.source_reference ? ` (${item.source_reference})` : ''}
                          </div>
                        )}
                      </details>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="Faltan textos de indicacion INVIMA por presentacion para este medicamento." />
                )}
              </Panel>

              <Panel title="Indicaciones UNIRS por presentacion" icon={<FlaskConical size={16} />} className="detail-panel unirs-original-panel">
                {report.unirs.items.length ? (
                  <div className="unirs-grid">
                    {report.unirs.items.map((item, index) => (
                      <details className="source-card source-detail" key={`${item.dci_concentracion}-${index}`}>
                        <summary>
                          <ChevronDown size={15} aria-hidden="true" />
                          <strong>{item.dci_concentracion}</strong>
                          <small>Abrir fuente</small>
                        </summary>
                        <span>{item.tipo_indicacion || 'Sin color'}</span>
                        <p>{item.indicaciones}</p>
                      </details>
                    ))}
                  </div>
                ) : <EmptyState text="No hay indicaciones UNIRS locales." />}
              </Panel>

              <Panel title="Politica de fuentes" icon={<Database size={16} />} className="side-panel source-policy-panel">
                <div className="source-policy">
                  {Object.entries(report.source_policy).map(([key, value]) => (
                    <p key={key}><strong>{key}</strong><span>{value}</span></p>
                  ))}
                </div>
              </Panel>
            </section>
          </>
        )}
      </main>
      <footer className="legal-footer">
        <div className="brand-mark">
          <div className="logo-placeholder">Logo Anaskai</div>
          <div>
            <strong>INVIMA Hemato-Oncologia</strong>
            <span>© 2026 Martin Munive / Anaskai. Todos los derechos reservados.</span>
            <a href="https://www.anaskai.com" target="_blank" rel="noreferrer">www.anaskai.com</a>
          </div>
        </div>
        <p>Aplicacion independiente. Integra fuentes publicas y locales para apoyo informativo; no reemplaza la consulta de la fuente oficial, el criterio clinico ni los procesos regulatorios aplicables. INVIMA, UNIRS y POS Populi conservan la titularidad y autoridad sobre sus datos oficiales.</p>
      </footer>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>,
);

