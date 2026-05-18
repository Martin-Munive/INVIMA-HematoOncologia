import React from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, BadgeCheck, ChevronDown, Database, FileSearch, FlaskConical, Search, ShieldCheck } from 'lucide-react';
import './styles.css';

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

function App() {
  const [query, setQuery] = React.useState('PACLITAXEL');
  const [report, setReport] = React.useState<DrugReport | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const loadReport = React.useCallback(async () => {
    const term = query.trim();
    if (!term) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/drugs/${encodeURIComponent(term)}/report?only_vigente=true`);
      if (!response.ok) {
        throw new Error(`API ${response.status}`);
      }
      setReport(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo consultar la API local');
    } finally {
      setLoading(false);
    }
  }, [query]);

  React.useEffect(() => {
    loadReport();
  }, []);

  const financed = Boolean(report?.pospopuli.items.some((item) => item.financiacion));
  const complete = Boolean(report?.completion.is_complete_for_current_sources);
  const firstDetail = report?.invima.details[0];
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
          <span>API LOCAL</span>
          <strong>{API_BASE}</strong>
        </div>
      </header>

      <main className="workspace">
        <section className="search-band">
          <div className="search-box">
            <Search size={20} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && loadReport()} />
            <button onClick={loadReport} disabled={loading}>{loading ? 'Consultando' : 'Buscar'}</button>
          </div>
          {error && <div className="error-line"><AlertTriangle size={16} /> {error}</div>}
        </section>

        {report && (
          <>
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
                <span>INVIMA vigente</span>
                <strong>{report.invima.details_count}</strong>
              </div>
              <div className="metric">
                <FlaskConical size={22} />
                <span>ATC principal</span>
                <strong>{firstDetail?.atc || 'Sin dato'}</strong>
              </div>
            </section>

            <section className="content-grid">
              <Panel title="Resumen regulatorio" icon={<FileSearch size={16} />} className="span-2">
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

              <Panel title="Perfil manual oncologico" icon={<Activity size={16} />}>
                {report.manual_profile ? (
                  <div className="text-list">
                    <h3>{report.manual_profile.nombre}</h3>
                    {splitBullets(report.manual_profile.efectos_adversos).slice(0, 8).map((line) => <p key={line}>{line}</p>)}
                    <div className="subsection-title">Extravasacion / manejo</div>
                    {splitBullets(report.manual_profile.extravasacion).map((line) => <p key={line}>{line}</p>)}
                  </div>
                ) : <EmptyState text="Sin perfil manual cargado." />}
              </Panel>

              <Panel title="Seguridad clinica curada" icon={<AlertTriangle size={16} />} className="span-2">
                {report.clinical_safety ? (
                  <div className="safety-layout">
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
                    <div className="source-note">Fuentes curadas: {report.clinical_safety.sources.map((source) => source.label).join('; ')}.</div>
                  </div>
                ) : <EmptyState text="Sin inmersion cientifica curada para este medicamento." />}
              </Panel>

              <Panel title="Indicaciones INVIMA por presentacion" icon={<ShieldCheck size={16} />} className="span-2 tall">
                <div className="table-list">
                  {report.invima.details.map((item) => (
                    <article key={`${item.expediente}-${item.cdgprod}`} className="detail-row">
                      <div className="detail-head">
                        <strong>{item.producto}</strong>
                        <span>{item.registro_sanitario}</span>
                      </div>
                      <div className="detail-meta">
                        <span>{item.forma_farmaceutica}</span>
                        <span>{item.principio_activo}</span>
                        <span>{item.concentracion}</span>
                      </div>
                      <p>{item.indicaciones}</p>
                    </article>
                  ))}
                </div>
              </Panel>

              <Panel title="UPC / POS Populi" icon={<BadgeCheck size={16} />}>
                {report.pospopuli.items.length ? report.pospopuli.items.map((item) => (
                  <div className="source-card" key={item.nombre}>
                    <strong>{item.nombre}</strong>
                    <span>{item.codigo_atc}</span>
                    <p>{item.financiacion || 'Sin financiacion registrada'}</p>
                  </div>
                )) : <EmptyState text="No hay resultados POS Populi locales." />}
              </Panel>

              <Panel title="UNIRS" icon={<FlaskConical size={16} />} className="span-2">
                {report.unirs.items.length ? (
                  <div className="unirs-grid">
                    {report.unirs.items.map((item, index) => (
                      <div className="source-card" key={`${item.dci_concentracion}-${index}`}>
                        <strong>{item.dci_concentracion}</strong>
                        <span>{item.tipo_indicacion || 'Sin color'}</span>
                        <p>{item.indicaciones}</p>
                      </div>
                    ))}
                  </div>
                ) : <EmptyState text="No hay indicaciones UNIRS locales." />}
              </Panel>

              <Panel title="Politica de fuentes" icon={<Database size={16} />}>
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
        INVIMA Hemato-Oncologia es una aplicacion independiente. Integra fuentes publicas y locales para apoyo informativo; no reemplaza la consulta de la fuente oficial, el criterio clinico ni los procesos regulatorios aplicables. INVIMA, UNIRS y POS Populi conservan la titularidad y autoridad sobre sus datos oficiales.
      </footer>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
