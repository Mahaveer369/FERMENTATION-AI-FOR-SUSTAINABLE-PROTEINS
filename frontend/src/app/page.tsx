"use client";

import Link from "next/link";
import { Beaker, LineChart, Leaf, Zap, ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Beaker className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">FermaGen AI</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-400 hover:text-white transition">Features</a>
            <a href="#how-it-works" className="text-gray-400 hover:text-white transition">How It Works</a>
            <a href="#sustainability" className="text-gray-400 hover:text-white transition">Sustainability</a>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/login" className="btn-secondary text-sm">
              Sign In
            </Link>
            <Link href="/signup" className="btn-primary text-sm">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-300">AI-Powered Precision Fermentation</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Accelerate</span> Your
              <br />Protein R&D
            </h1>

            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Simulate fermentation experiments, optimize protein formulations, and reduce
              R&D time by 40-50% with our AI-powered platform.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup" className="btn-primary text-lg px-8 py-4 flex items-center justify-center gap-2">
                Start Free Trial <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="#demo" className="btn-secondary text-lg px-8 py-4">
                Watch Demo
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20">
            {[
              { value: "40-50%", label: "R&D Time Reduction" },
              { value: "≥85%", label: "Prediction Accuracy" },
              { value: "<5s", label: "Simulation Runtime" },
              { value: "100%", label: "Free & Open APIs" },
            ].map((stat, i) => (
              <div key={i} className="card text-center">
                <div className="text-3xl font-bold gradient-text mb-2">{stat.value}</div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Everything you need to accelerate sustainable protein development
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Beaker className="w-8 h-8" />,
                title: "Fermentation Simulation",
                description: "AI-powered predictions for yield, energy, and CO₂ based on microbe, substrate, temperature, pH, and duration.",
                color: "from-green-500 to-emerald-600"
              },
              {
                icon: <LineChart className="w-8 h-8" />,
                title: "Multi-Objective Optimization",
                description: "Genetic algorithm optimization to maximize yield while minimizing time and carbon footprint.",
                color: "from-blue-500 to-cyan-600"
              },
              {
                icon: <Leaf className="w-8 h-8" />,
                title: "Sustainability Scoring",
                description: "Real-time sustainability metrics and CO₂ savings calculations for eco-conscious R&D.",
                color: "from-emerald-500 to-teal-600"
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: "Protein Analysis",
                description: "BioPython-powered sequence analysis with molecular weight, pI, and stability predictions.",
                color: "from-purple-500 to-violet-600"
              },
              {
                icon: <Sparkles className="w-8 h-8" />,
                title: "AI Explanations",
                description: "Get scientific explanations for why certain formulations work better than others.",
                color: "from-pink-500 to-rose-600"
              },
              {
                icon: <LineChart className="w-8 h-8" />,
                title: "Experiment History",
                description: "Track all experiments, compare results, and export data for publication.",
                color: "from-amber-500 to-orange-600"
              },
            ].map((feature, i) => (
              <div key={i} className="card group">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              From parameters to optimized formulation in seconds
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "1", title: "Input Parameters", desc: "Select microbe, substrate, temperature, pH, and duration" },
              { step: "2", title: "AI Simulation", desc: "ML models predict yield, energy, and CO₂ footprint" },
              { step: "3", title: "Optimization", desc: "Multi-objective algorithm finds optimal conditions" },
              { step: "4", title: "Insights", desc: "Get AI explanations and sustainability recommendations" },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="card text-center py-16 glow-green">
            <h2 className="text-4xl font-bold mb-4">Ready to Transform Your R&D?</h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Join researchers worldwide using AI to accelerate sustainable protein development.
            </p>
            <Link href="/signup" className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2">
              Get Started Free <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Beaker className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold">FermaGen AI</span>
          </div>

          <p className="text-gray-500 text-sm">
            © 2026 FermaGen AI. Open-source precision fermentation platform.
          </p>

          <div className="flex gap-6">
            <a href="#" className="text-gray-400 hover:text-white text-sm transition">GitHub</a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition">Docs</a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition">Contact</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
