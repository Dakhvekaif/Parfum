import { Search, ShoppingBag, User, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="sticky top-0 z-50 bg-brand-black text-brand-white border-b border-brand-darkGray">
            <div className="container flex items-center justify-between h-20 px-4">
                {/* Mobile Menu Button */}
                <button
                    className="lg:hidden p-2 hover:text-brand-gold transition-colors"
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? <X size={24} /> : <Menu size={24} />}
                </button>

                {/* Left Icons (Desktop) */}
                <div className="hidden lg:flex items-center space-x-6">
                    <button className="hover:text-brand-gold transition-colors">
                        <Search size={20} />
                    </button>
                </div>

                {/* Logo */}
                <Link to="/" className="flex flex-col items-center">
                    <h1 className="text-2xl lg:text-3xl font-serif tracking-[0.2em] font-bold">
                        SWISS<span className="text-brand-gold">A</span>ROMA
                    </h1>
                </Link>

                {/* Right Icons */}
                <div className="flex items-center space-x-4 lg:space-x-6">
                    <button className="hidden lg:block hover:text-brand-gold transition-colors">
                        <User size={20} />
                    </button>
                    <button className="hover:text-brand-gold transition-colors relative">
                        <ShoppingBag size={20} />
                        <span className="absolute -top-1 -right-1 bg-brand-gold text-brand-black text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
                            0
                        </span>
                    </button>
                </div>
            </div>

            {/* Desktop Navigation Links */}
            <div className="hidden lg:block border-t border-brand-darkGray bg-brand-black/95">
                <div className="container flex justify-center py-4">
                    <ul className="flex space-x-8 text-sm uppercase tracking-widest font-medium">
                        {['Perfumes', 'Oils', 'Gift Sets', 'Home Scents', 'Bath & Body'].map((item) => (
                            <li key={item}>
                                <Link to="/" className="hover:text-brand-gold transition-colors relative group">
                                    {item}
                                    <span className="absolute left-0 bottom-0 w-0 h-[1px] bg-brand-gold transition-all duration-300 group-hover:w-full" />
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="lg:hidden bg-brand-black border-t border-brand-darkGray overflow-hidden"
                    >
                        <ul className="flex flex-col p-4 space-y-4 text-center">
                            {['Perfumes', 'Oils', 'Gift Sets', 'Home Scents', 'Bath & Body', 'Account', 'Search'].map((item) => (
                                <li key={item}>
                                    <Link
                                        to="/"
                                        className="block py-2 text-sm uppercase tracking-widest hover:text-brand-gold"
                                        onClick={() => setIsOpen(false)}
                                    >
                                        {item}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
