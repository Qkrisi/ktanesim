use crate::prelude::*;
use serenity::model::prelude::*;
use serenity::prelude::*;
use std::boxed::FnBox;
use strum_macros::Display;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Display)]
#[strum(serialize_all = "snake_case")]
pub enum ModuleOrigin {
    Vanilla,
    Modded,
    Novelty,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Display)]
#[strum(serialize_all = "snake_case")]
pub enum ModuleCategory {
    Solvable,
    Needy,
    Boss,
}

pub struct ModuleDescriptor {
    pub identifier: &'static str,
    pub aliases: &'static [&'static str],
    pub constructor: ModuleNew,
    pub origin: ModuleOrigin,
    pub category: ModuleCategory,
    pub rule_seed: bool,
}

// Comparing constructor is enough, the rest is just metadata. This could be derived, but ModuleNew
// does not implement PartialEq because of higher-ranked trait bounds caused by the references.
// Compare rust-lang/rust#46989
impl Eq for ModuleDescriptor {}
impl PartialEq for ModuleDescriptor {
    fn eq(&self, other: &Self) -> bool {
        self.constructor as usize == other.constructor as usize
    }
}

use std::hash::{Hash, Hasher};
impl Hash for ModuleDescriptor {
    fn hash<H: Hasher>(&self, state: &mut H) {
        (self.constructor as usize).hash(state);
    }
}

use std::fmt;
impl fmt::Debug for ModuleDescriptor {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "<module {:?}>", self.identifier)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ModuleGroup {
    Single(&'static ModuleDescriptor),
    Category(ModuleCategory),
    Origin(ModuleOrigin),
    Ruleseed,
    All,
}

use std::collections::HashSet;

impl ModuleGroup {
    pub fn add_to_set(&self, set: &mut HashSet<&'static ModuleDescriptor>) {
        fn add_matching<F>(set: &mut HashSet<&'static ModuleDescriptor>, f: F)
        where
            F: Fn(&'static ModuleDescriptor) -> bool,
        {
            for module in MODULE_GROUPS
                .values()
                .filter_map(|&group| {
                    if let ModuleGroup::Single(module) = group {
                        Some(module)
                    } else {
                        None
                    }
                })
                .filter(|&m| f(m))
            {
                set.insert(module);
            }
        }

        match *self {
            ModuleGroup::Single(module) => {
                set.insert(module);
            }
            ModuleGroup::Category(cat) => add_matching(set, |m| m.category == cat),
            ModuleGroup::Origin(origin) => add_matching(set, |m| m.origin == origin),
            ModuleGroup::Ruleseed => add_matching(set, |m| m.rule_seed),
            ModuleGroup::All => add_matching(set, |_| true),
        }
    }

    pub fn remove_from_set(&self, set: &mut HashSet<&'static ModuleDescriptor>) {
        match *self {
            ModuleGroup::Single(module) => {
                set.remove(module);
            }
            ModuleGroup::Category(cat) => set.retain(|m| m.category != cat),
            ModuleGroup::Origin(origin) => set.retain(|m| m.origin != origin),
            ModuleGroup::Ruleseed => set.retain(|m| !m.rule_seed),
            ModuleGroup::All => set.clear(),
        }
    }
}

impl fmt::Display for ModuleGroup {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ModuleGroup::Single(descriptor) => f.write_str(descriptor.identifier),
            ModuleGroup::Category(cat) => cat.fmt(f),
            ModuleGroup::Origin(origin) => origin.fmt(f),
            ModuleGroup::Ruleseed => f.write_str("ruleseedable"),
            ModuleGroup::All => f.write_str("all"),
        }
    }
}

pub type ModuleNew = fn(bomb: &mut Bomb) -> Box<dyn Module>;

use phf_macros::phf_map;
use ModuleGroup::Single;

/// A perfect hash map of all modules and module groups
pub static MODULE_GROUPS: phf::Map<&'static str, ModuleGroup> = phf_map! {
    "wires"       => Single(&wires::DESCRIPTOR),
    "simplewires" => Single(&wires::DESCRIPTOR),

    "vanilla"      => VANILLA_MODULES,
    "base"         => VANILLA_MODULES,
    "unmodded"     => VANILLA_MODULES,
    "solvable"     => SOLVABLE_MODULES,
    "regular"      => SOLVABLE_MODULES,
    "normal"       => SOLVABLE_MODULES,
    "ruleseed"     => ModuleGroup::Ruleseed,
    "ruleseedable" => ModuleGroup::Ruleseed,
    "all"          => ModuleGroup::All,
    "any"          => ModuleGroup::All,
};

#[cfg(test)]
#[test]
fn module_identifiers_consistent() {
    for (&key, group) in MODULE_GROUPS.entries() {
        if let Single(module) = group {
            assert_eq!(Some(group), MODULE_GROUPS.get(module.identifier));
            assert!(module.identifier == key || module.aliases.contains(&key));
        }
    }
}

static VANILLA_MODULES: ModuleGroup = ModuleGroup::Origin(ModuleOrigin::Vanilla);
static SOLVABLE_MODULES: ModuleGroup = ModuleGroup::Category(ModuleCategory::Solvable);

pub mod wires;

pub const MODULE_SIZE: i32 = 348;
pub type Render = Box<dyn FnBox() -> (Vec<u8>, RenderType)>;

pub trait Module: Send + Sync {
    fn handle_command(&mut self, bomb: &mut Bomb, user: UserId, command: &str) -> EventResponse;
    fn view(&self, light: SolveLight) -> Render;
}

pub struct EventResponse {
    render: Option<Render>,
    message: Option<String>,
}

#[derive(Copy, Clone, PartialEq, Eq, Debug, Display)]
#[strum(serialize_all = "snake_case")]
pub enum RenderType {
    PNG,
    GIF,
}

#[derive(Copy, Clone, PartialEq, Eq)]
pub enum SolveLight {
    Normal,
    Solved,
    Strike,
}

use cairo::{Context, ImageSurface};
/// Return an `ImageSurface` with a blank module drawn on it, along with a `Context` that can be used
/// to draw any further graphics.
pub fn module_canvas(status: SolveLight) -> (ImageSurface, Context) {
    let surface = ImageSurface::create(cairo::Format::ARgb32, MODULE_SIZE, MODULE_SIZE).unwrap();
    let ctx = Context::new(&surface);

    ctx.set_line_join(cairo::LineJoin::Round);

    ctx.rectangle(5.0, 5.0, 338.0, 338.0);
    ctx.set_source_rgb(1.0, 1.0, 1.0);
    ctx.fill_preserve();
    ctx.set_source_rgb(0.0, 0.0, 0.0);
    ctx.stroke();

    ctx.arc(298.0, 40.5, 15.0, 0.0, 2.0 * std::f64::consts::PI);

    use SolveLight::*;
    match status {
        Normal => ctx.set_source_rgb(1.0, 1.0, 1.0),
        Solved => ctx.set_source_rgb(0.0, 1.0, 0.0),
        Strike => ctx.set_source_rgb(1.0, 0.0, 0.0),
    }

    ctx.fill_preserve();
    ctx.set_source_rgb(0.0, 0.0, 0.0);
    ctx.stroke();

    (surface, ctx)
}

/// Given an `ImageSurface`, return what an implementation of `Render` should.
pub fn output_png(surface: ImageSurface) -> (Vec<u8>, RenderType) {
    let mut png = std::io::Cursor::new(vec![]);
    surface.write_to_png(&mut png).unwrap();
    (png.into_inner(), RenderType::PNG)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn render_type_is_lowercase() {
        assert_eq!(RenderType::PNG.to_string(), "png");
    }
}