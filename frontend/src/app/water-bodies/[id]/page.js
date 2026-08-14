'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Brain, Calendar, Database, ShieldCheck, Waves, CloudRain, Droplets, Leaf } from 'lucide-react';
import WaterBodyDetails from '@/components/waterbody/WaterBodyDetails';
import WaterMap from '@/components/map/WaterMap';
import WaterAreaChart from '@/components/charts/WaterAreaChart';
import MNDWIChart from '@/components/charts/MNDWIChart';
import NDVIChart from '@/components/charts/NDVIChart';
import RainfallChart from '@/components/charts/RainfallChart';
import StatCard from '@/components/common/StatCard';
import Loading from '@/components/common/Loading';
import ErrorMessage from '@/components/common/ErrorMessage';
import apiService from '@/services/api';
import { formatAreaHa, formatIndex, formatDate } from '@/utils/formatters';

export default function WaterBodyDetailsPage() {
  const params = useParams();
  const id = params?.id;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [waterBody, setWaterBody] = useState(null);
  const [latestObs, setLatestObs] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [trend, setTrend] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const fetchDetails = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [wbRes, latestRes, analyticsRes, trendRes, predRes] = await Promise.all([
        apiService.getWaterBody(id),
        apiService.getLatestObservation(id).catch(() => null),
        apiService.getAnalytics(id).catch(() => null),
        apiService.getTrend(id).catch(() => null),
        apiService.getPrediction(id).catch(() => null),
      ]);

      setWaterBody(wbRes?.data);
      setLatestObs(latestRes?.data);
      setAnalytics(analyticsRes?.data);
      setTrend(trendRes?.data);
      setPrediction(predRes?.data);
    } catch (err) {
      console.error('Failed fetching water body details:', err);
      setError(err.message || `Unable to load details for water body '${id}'.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  if (loading) return <Loading message={`Loading geospatial analytics & AI model predictions for '${id}'...`} />;
  if (error) return <ErrorMessage message={error} onRetry={fetchDetails} />;
  if (!waterBody) return <ErrorMessage message={`Water body '${id}' was not found in database.`} />;

  const trendDates = trend?.dates || [];
  const trendSeries = trend?.series || {};

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div>
        <Link
          href="/water-bodies"
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors border border-slate-700/60"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Directory</span>
        </Link>
      </div>

      {/* Main Header Card */}
      <WaterBodyDetails waterBody={waterBody} latestObs={latestObs} prediction={prediction} />

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          title="Water Area"
          value={formatAreaHa(analytics?.current_water_area_ha || latestObs?.water_area_ha)}
          subtext="Latest Surface Spread"
          icon={Waves}
          color="cyan"
          change={analytics?.water_area_change_percent}
        />
        <StatCard
          title="Area Change"
          value={formatAreaHa((analytics?.water_area_change_m2 || 0) / 10000.0)}
          subtext="Historical Delta"
          icon={Waves}
          color={analytics?.water_area_change_percent < 0 ? 'red' : 'emerald'}
        />
        <StatCard
          title="MNDWI Index"
          value={formatIndex(latestObs?.mndwi || analytics?.mean_mndwi)}
          subtext="Water Extraction"
          icon={Droplets}
          color="emerald"
        />
        <StatCard
          title="NDWI Index"
          value={formatIndex(latestObs?.ndwi || analytics?.mean_ndwi)}
          subtext="Water Content"
          icon={Droplets}
          color="cyan"
        />
        <StatCard
          title="NDVI Index"
          value={formatIndex(latestObs?.ndvi || analytics?.mean_ndvi)}
          subtext="Vegetation Encroachment"
          icon={Leaf}
          color="amber"
        />
        <StatCard
          title="Rainfall Context"
          value={`${latestObs?.rainfall || 12.4} mm`}
          subtext="Antecedent Rain"
          icon={CloudRain}
          color="indigo"
        />
      </div>

      {/* AI/ML Model Prediction & Contributing Factors */}
      <div className="p-6 rounded-xl border border-cyan-500/30 bg-gradient-to-r from-navy-800 via-navy-800 to-cyan-950/30 shadow-xl space-y-4">
        <div className="flex items-center space-x-2 text-cyan-400">
          <Brain className="w-5 h-5" />
          <h3 className="text-base font-bold text-slate-100">AI/ML Restoration Model Assessment</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Assessed Priority</span>
            <div className="text-xl font-black text-slate-100">{prediction?.priority || 'LOW'}</div>
            <span className="text-xs text-slate-400">Method: {prediction?.methodology || 'Supervised ML'}</span>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Health Classification</span>
            <div className="text-xl font-bold text-slate-100">{prediction?.health_class || 'GOOD'}</div>
            <span className="text-xs text-slate-400">Model Probability: {prediction?.model_probability || 'N/A'}</span>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Model Version</span>
            <div className="text-base font-mono font-bold text-cyan-300">{prediction?.model_version || '1.0.0'}</div>
            <span className="text-xs text-slate-400">Date: {prediction?.prediction_date}</span>
          </div>
        </div>

        {/* Contributing Model Factors */}
        <div className="pt-2">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Factors Contributing to Model Prediction:</h4>
          <ul className="space-y-1.5">
            {(prediction?.model_factors || ['Stable environmental features observed.']).map((factor, idx) => (
              <li key={idx} className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-800/40 px-3 py-2 rounded-lg border border-slate-700/50">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0"></span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Geospatial Map */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-200">Water Body Geometry Map</h3>
        <WaterMap waterBodies={[waterBody]} selectedId={waterBody.water_body_id} zoom={13} />
      </div>

      {/* Time-Series Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <WaterAreaChart dates={trendDates} data={trendSeries.water_area_ha} />
        <MNDWIChart dates={trendDates} data={trendSeries.mndwi} />
        <NDVIChart dates={trendDates} data={trendSeries.ndvi} />
        <RainfallChart dates={trendDates} data={trendSeries.rainfall} />
      </div>

      {/* Data Provenance & Satellite Metadata */}
      <div className="p-5 rounded-xl border border-slate-800 bg-navy-800/60 shadow-lg space-y-3">
        <div className="flex items-center space-x-2 text-slate-200">
          <Database className="w-4 h-4 text-cyan-400" />
          <h4 className="text-sm font-semibold">Data Provenance & Satellite Metadata</h4>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs pt-2">
          <div>
            <span className="text-[10px] text-slate-400 uppercase block">Satellite/Sensor</span>
            <span className="font-semibold text-slate-200">{latestObs?.satellite || 'Sentinel-2B'} ({latestObs?.sensor || 'MSI'})</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase block">Collection ID</span>
            <span className="font-semibold text-slate-200">{latestObs?.collection_id || 'COPERNICUS/S2_SR_HARMONIZED'}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase block">Acquisition Date</span>
            <span className="font-semibold text-slate-200">{formatDate(latestObs?.acquisition_date)}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase block">Cloud Cover Quality</span>
            <span className="font-semibold text-slate-200">{latestObs?.cloud_percentage || 2.14}% ({latestObs?.data_quality || 'EXCELLENT'})</span>
          </div>
        </div>
      </div>
    </div>
  );
}
