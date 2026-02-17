import { Facebook, Instagram, Twitter } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="bg-brand-black text-white pt-16 pb-8 border-t border-brand-darkGray">
            <div className="container px-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
                {/* Brand Column */}
                <div>
                    <h2 className="text-2xl font-serif font-bold mb-6">
                        P<span className="text-brand-gold">A</span>RFUM <span className="text-xs align-top">QA</span>
                    </h2>
                    <p className="text-brand-gray/80 text-sm leading-relaxed mb-6">
                        Discover the essence of luxury with our curated collection of premium fragrances.
                        Crafted for those who appreciate the finer things in life.
                    </p>
                    <div className="flex space-x-4">
                        <a href="#" className="w-10 h-10 rounded-full bg-brand-darkGray flex items-center justify-center hover:bg-brand-gold hover:text-brand-black transition-colors">
                            <Facebook size={18} />
                        </a>
                        <a href="#" className="w-10 h-10 rounded-full bg-brand-darkGray flex items-center justify-center hover:bg-brand-gold hover:text-brand-black transition-colors">
                            <Instagram size={18} />
                        </a>
                        <a href="#" className="w-10 h-10 rounded-full bg-brand-darkGray flex items-center justify-center hover:bg-brand-gold hover:text-brand-black transition-colors">
                            <Twitter size={18} />
                        </a>
                    </div>
                </div>

                {/* Quick Links */}
                <div>
                    <h3 className="text-lg font-serif mb-6 text-brand-gold">Quick Links</h3>
                    <ul className="space-y-4 text-sm text-brand-gray/80">
                        {['About Us', 'Contact Us', 'Shipping Policy', 'Returns & Exchanges', 'Privacy Policy'].map(item => (
                            <li key={item}>
                                <a href="#" className="hover:text-brand-gold transition-colors">{item}</a>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Categories */}
                <div>
                    <h3 className="text-lg font-serif mb-6 text-brand-gold">Collections</h3>
                    <ul className="space-y-4 text-sm text-brand-gray/80">
                        {['Men Perfumes', 'Women Perfumes', 'Unisex', 'Gift Sets', 'Oils & Musk'].map(item => (
                            <li key={item}>
                                <a href="#" className="hover:text-brand-gold transition-colors">{item}</a>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Newsletter */}
                <div>
                    <h3 className="text-lg font-serif mb-6 text-brand-gold">Newsletter</h3>
                    <p className="text-brand-gray/80 text-sm mb-4">
                        Subscribe to receive updates, access to exclusive deals, and more.
                    </p>
                    <form className="space-y-3">
                        <input
                            type="email"
                            placeholder="Enter your email"
                            className="w-full bg-brand-darkGray border border-brand-gray/20 px-4 py-3 text-sm focus:outline-none focus:border-brand-gold text-white placeholder:text-gray-500"
                        />
                        <button className="w-full bg-brand-gold text-brand-black font-semibold uppercase tracking-widest text-xs py-3 hover:bg-white transition-colors">
                            Subscribe
                        </button>
                    </form>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="container px-4 pt-8 border-t border-brand-darkGray flex flex-col md:flex-row justify-between items-center text-xs text-brand-gray/60">
                <p>&copy; 2024 SwissAroma. All rights reserved.</p>
                <div className="flex space-x-6 mt-4 md:mt-0">
                    <span>Terms of Service</span>
                    <span>Privacy Policy</span>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
