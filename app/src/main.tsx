import React from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, BadgeCheck, ChevronDown, Database, FileSearch, FlaskConical, Search, ShieldCheck } from 'lucide-react';
import './styles.css';

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
  };
  unirs: { count: number; items: UnirsItem[] };
  pospopuli: { count: number; items: PosPopuliItem[] };
  clinical_safety: ClinicalSafety;
  source_policy: Record<string, string>;
};

type DrugSuggestion = {
  name: string;
  sources: string[];
  count: number;
};

const API_BASE = 'http://127.0.0.1:8000';

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
  }[];
};

const INDICATION_PATTERNS: { label: string; pattern: RegExp }[] = [
  { label: 'Cancer de mama metastasico', pattern: /CANCER DE MAMA METASTASICO/i },
  { label: 'Cancer de mama', pattern: /CANCER DE MAMA(?! METASTASICO)|CARCINOMA DE MAMA|CARCINOMA AVANZADO DE SENO/i },
  { label: 'Cancer de ovario', pattern: /CANCER DE OVARIO|CANCER METASTASICO DEL OVARIO|CARCINOMA AVANZADO DEL OVARIO|CARCINOMA METASTASICO DE OVARIO/i },
  { label: 'Cancer de pulmon no microcitico / NSCLC', pattern: /CANCER DE PULMON NO MICROCITICO|CANCER DE PULMON DE CELULAS NO[- ]PEQUENAS|NSCLC/i },
  { label: 'Adenocarcinoma de pancreas metastasico', pattern: /ADENOCARCINOMA DE PANCREAS METASTASICO/i },
  { label: 'Sarcoma de Kaposi relacionado con SIDA', pattern: /SARCOMA DE KAPOSI/i },
];

const UNIRS_INDICATION_PATTERNS: { label: string; pattern: RegExp }[] = [
  ...INDICATION_PATTERNS,
  { label: 'Adenocarcinoma de primario desconocido', pattern: /ADENOCARCINOMA DE PRIMARIO DESCONOCIDO|CARCINOMAS? DE ORIGEN PRIMARIO DESCONOCIDO/i },
  { label: 'Cancer de cervix', pattern: /CANCER DE CERVIX|CANCER CERVIX/i },
  { label: 'Cancer de endometrio', pattern: /CANCER DE ENDOMETRIO/i },
  { label: 'Cancer de esofago', pattern: /CANCER ESOFAGO|CANCER DE ESOFAGO/i },
  { label: 'Cancer gastrico', pattern: /CANCER GASTRICO/i },
  { label: 'Malignidad timica / timoma', pattern: /MALIGNIDAD TIMICA|TIMOMAS?|CARCINOMAS TIMICOS/i },
];

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
    const indicationText = normalizeSearchText(item.indicaciones || '');
    UNIRS_INDICATION_PATTERNS.forEach(({ label, pattern }) => {
      if (!pattern.test(indicationText)) return;
      const current = grouped.get(label) ?? { label, items: [] };
      const alreadyListed = current.items.some(
        (entry) => entry.dci_concentracion === item.dci_concentracion && entry.tipo_indicacion === item.tipo_indicacion,
      );
      if (!alreadyListed) {
        current.items.push({
          dci_concentracion: item.dci_concentracion,
          forma_farmaceutica: item.forma_farmaceutica,
          tipo_indicacion: item.tipo_indicacion || 'Sin clasificacion',
        });
      }
      grouped.set(label, current);
    });
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
    },
    unirs: {
      count: raw.unirs?.count ?? 0,
      items: raw.unirs?.items ?? [],
    },
    pospopuli: {
      count: raw.pospopuli?.count ?? 0,
      items: raw.pospopuli?.items ?? [],
    },
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
  if (report.clinical_safety) return 'Perfil clinico curado disponible para seguridad, hipersensibilidad y manejo de extravasacion.';
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
          <strong>{financed ? 'Financiado' : 'No encontrado'}</strong>
          {posNames && <small>{posNames}</small>}
        </div>
        <div>
          <span>ATC</span>
          <strong>{firstDetail?.atc || 'Sin dato'}</strong>
          <small>{firstDetail?.forma_farmaceutica || 'Detalle INVIMA'}</small>
        </div>
        <div>
          <span>Detalles INVIMA</span>
          <strong>{report.invima.details_count}</strong>
          <small>Presentaciones con texto regulatorio</small>
        </div>
        <div>
          <span>UNIRS</span>
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

  const loadReport = React.useCallback(async (termOverride?: string) => {
    const term = (termOverride ?? query).trim();
    if (!term) return;
    setQuery(term);
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
  const regulatorySummary = report ? buildRegulatorySummary(report.invima.details) : [];
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
                    onMouseDown={(event) => {
                      event.preventDefault();
                      loadReport(item.name);
                    }}
                    type="button"
                  >
                    <strong>{item.name}</strong>
                    <span>{item.sources.join(' · ')} · {item.count} coincidencias</span>
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
                <strong>{financed ? 'Financiado' : 'No encontrado'}</strong>
              </div>
              <div className="metric">
                <Database size={22} />
                <span>INVIMA local</span>
                <strong>{report.invima.details_count}</strong>
              </div>
              <div className="metric">
                <FlaskConical size={22} />
                <span>UNIRS</span>
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
                <div className="subsection-title">Patologias detectadas en indicaciones INVIMA vigentes</div>
                {regulatorySummary.length ? (
                  <div className="regulatory-summary">
                    {regulatorySummary.map((item) => (
                      <details key={item.label} className="indication-summary-section">
                        <summary className="indication-summary-head">
                          <ChevronDown size={16} aria-hidden="true" />
                          <strong>{item.label}</strong>
                          <span>{item.presentations.length} presentaciones</span>
                          <small>Abrir</small>
                        </summary>
                        <div className="presentation-list">
                          <div className="presentation-list-head">
                            <span>Producto</span>
                            <span>Concentracion</span>
                            <span>Registro</span>
                          </div>
                          {item.presentations.map((presentation) => (
                            <div className="presentation-line" key={`${item.label}-${presentation.producto}-${presentation.registro_sanitario}`}>
                              <span>{presentation.producto}</span>
                              <span>{displayConcentration(presentation)}</span>
                              <span>{presentation.registro_sanitario}</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="No se detectaron patologias en el texto local de indicaciones INVIMA." />
                )}
                <div className="subsection-title">UNIRS en el mismo informe</div>
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
                <div className="source-note">Fuente: derivado del campo de indicaciones INVIMA por presentacion. Confirmar el texto completo en el panel inferior antes de autorizar uso.</div>
                {report.completion.missing_sources.length > 0 && (
                  <div className="warning-box">Faltan fuentes: {report.completion.missing_sources.join(', ')}</div>
                )}
              </Panel>

              <Panel title="Perfil clinico y seguridad" icon={<AlertTriangle size={16} />} className="clinical-panel">
                {report.clinical_safety || report.manual_profile ? (
                  <div className="safety-layout">
                    {report.manual_profile && (
                      <div className="safety-column clinical-baseline">
                        <div className="subsection-title">Perfil local</div>
                        <h3>{report.manual_profile.nombre}</h3>
                        {report.manual_profile.mecanismo && <p>{report.manual_profile.mecanismo}</p>}
                        {report.manual_profile.indicacion_manual && (
                          <details className="safety-group">
                            <summary><ChevronDown size={15} aria-hidden="true" /> <span>Indicaciones resumidas locales</span><small>Abrir</small></summary>
                            {splitBullets(report.manual_profile.indicacion_manual).map((line) => <p key={line}>{line}</p>)}
                          </details>
                        )}
                      </div>
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
                      Fuentes curadas: {[...(report.clinical_safety.mechanism_sources ?? []), ...report.clinical_safety.sources].map((source) => source.label).join('; ')}.
                    </div>
                      </>
                    )}
                    {!report.clinical_safety && report.manual_profile && (
                      <div className="source-note">Este medicamento solo tiene perfil manual local. Falta inmersion cientifica curada para seguridad por sistema, hipersensibilidad y extravasacion.</div>
                    )}
                  </div>
                ) : <EmptyState text="Sin perfil clinico local ni inmersion cientifica curada para este medicamento." />}
              </Panel>

              <Panel title="Indicaciones INVIMA por presentacion" icon={<ShieldCheck size={16} />} className="detail-panel">
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
                        <p>{item.indicaciones}</p>
                      </details>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="Faltan textos de indicacion INVIMA por presentacion para este medicamento." />
                )}
              </Panel>

              <Panel title="UNIRS texto original" icon={<FlaskConical size={16} />} className="detail-panel">
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

              <Panel title="Politica de fuentes" icon={<Database size={16} />} className="side-panel">
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
