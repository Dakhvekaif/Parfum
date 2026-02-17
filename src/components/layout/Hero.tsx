import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight } from 'lucide-react';

const slides = [
    {
        id: 1,
        title: "Every perfume set is a wish",
        subtitle: "each fragrance a note of happiness just for you",
        image: "url('https://images.unsplash.com/photo-1541643600914-78b084683601?q=80&w=2000&auto=format&fit=crop')", // Placeholder luxury perfume image
        cta: "Explore Collection"
    },
    {
        id: 2,
        title: "Scents for...? 1QAR",
        subtitle: "Yes, that's right!",
        image: "url('https://images.unsplash.com/photo-1594035910387-fea477942654?q=80&w=2000&auto=format&fit=crop')",
        cta: "Shop Now"
    },
    {
        id: 3,
        title: "Discover fragrance in its purest form",
        subtitle: "Alcohol free allure",
        image: "url('https://images.unsplash.com/photo-1615634260167-c8cdede054de?q=80&w=2000&auto=format&fit=crop')",
        cta: "Subscribe Now"
    }
];

const Hero = () => {
    const [current, setCurrent] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrent((prev) => (prev + 1) % slides.length);
        }, 5000);
        return () => clearInterval(timer);
    }, []);

    return (
        <section className="relative h-[85vh] w-full bg-brand-black overflow-hidden text-brand-white">
            <AnimatePresence mode="wait">
                <motion.div
                    key={current}
                    initial={{ opacity: 0, scale: 1.1 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 1.5 }}
                    className="absolute inset-0 bg-cover bg-center"
                    style={{ backgroundImage: slides[current].image }}
                >
                    <div className="absolute inset-0 bg-black/30" /> {/* Lighter overlay */}
                </motion.div>
            </AnimatePresence>

            <div className="relative h-full flex flex-col justify-center items-center text-center px-4 z-10">
                <motion.div
                    key={`text-${current}`}
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                    className="max-w-4xl"
                >
                    <h2 className="text-5xl lg:text-7xl font-serif mb-6 leading-tight tracking-wide drop-shadow-md">
                        {slides[current].title}
                    </h2>
                    <p className="text-xl lg:text-3xl font-light tracking-wide mb-12 opacity-90 drop-shadow-sm">
                        {slides[current].subtitle}
                    </p>
                    <button className="bg-white text-brand-black border-2 border-white px-10 py-4 uppercase tracking-[0.2em] text-sm font-bold hover:bg-transparent hover:text-white transition-all duration-300 flex items-center mx-auto gap-3">
                        {slides[current].cta}
                        <ChevronRight size={18} />
                    </button>
                </motion.div>
            </div>
            {/* Dots Indicator */}
            <div className="absolute bottom-8 right-8 flex space-x-3">
                {slides.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => setCurrent(index)}
                        className={`w-3 h-3 rounded-full transition-all duration-300 ${index === current ? 'bg-brand-white w-8' : 'bg-white/50'
                            }`}
                    />
                ))}
            </div>
        </section>
    );
};

export default Hero;
